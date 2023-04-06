from torch.multiprocessing import Queue
import tqdm
import torch
from typing import List
from ml_gym.multiprocessing.job import JobType, Job, JobCollection, JobStatusSubscriberIF
from ml_gym.multiprocessing.worker import WorkerProcessWrapper
from ml_gym.multiprocessing.job import JobStatus
from ml_gym.persistency.logging import JobStatusLogger, MLgymStatusLoggerCollectionConstructable


class JobStatusLoggingSubscriber(JobStatusSubscriberIF):

    def __init__(self, logger: JobStatusLogger):
        self._logger = logger

    def callback_job_event(self, job: Job):
        representation = {"job_id": job.job_id, "job_type": job.job_type, "grid_search_id": job.grid_search_id,
                          "experiment_id": job.experiment_id, "status": job.status,
                          "starting_time": job.starting_time, "finishing_time": job.finishing_time, "error": job.error,
                          "stacktrace": job.stacktrace}
        self._logger.log_job_status(**representation)


class Pool:
    def __init__(self, num_processes: int, devices: List[torch.device],
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable, max_jobs_per_process: int = 1):
        self.num_processes = num_processes
        self.job_q = Queue()
        self.job_update_q = Queue()
        self.devices = devices
        self.worker_processes = []
        self.max_jobs_per_process = max_jobs_per_process
        logger_collection = logger_collection_constructable.construct()
        self.job_status_logger = JobStatusLogger(logger=logger_collection)
        subscriber = JobStatusLoggingSubscriber(self.job_status_logger)
        self.job_collection = JobCollection()
        self.job_collection.add_subscriber(subscriber)

    def add_job(self, job: Job):
        self.job_q.put(job)
        self.job_collection.add_or_update_job(job)

    def add_jobs(self, jobs: List[Job]):
        for job in tqdm.tqdm(jobs):
            self.job_q.put(job)
            self.job_collection.add_or_update_job(job)

    def run(self):
        # we have to add the termination jobs at the end of the queue such that the processes stop working and don't get stuck in jobs_q.get()
        termination_jobs = [Job(job_id=i+len(self.job_collection), fun=None, blueprint=None, param_dict=None,
                                job_type=JobType.TERMINATE) for i in range(self.num_processes)]
        self.add_jobs(termination_jobs)
        # create and start worker processes
        for process_id in tqdm.tqdm(range(self.num_processes), desc="Creating processes"):
            self.create_or_replace_process(process_id, self.max_jobs_per_process)
        for p in tqdm.tqdm(self.worker_processes, desc="Starting processes"):
            p.start()
        # wait until all jobs are done
        while not self.job_collection.done:
            updated_job: Job = self.job_update_q.get()
            self.job_collection.add_or_update_job(updated_job)
            if updated_job.status == JobStatus.DONE and updated_job.error is not None:
                pass
            elif updated_job.status == JobStatus.DONE:
                pass
            if updated_job.status == JobStatus.DONE and updated_job.job_type == JobType.CALC:
                self.worker_processes[updated_job.executing_process_id].recreate_process_if_done()

        self.job_status_logger.disconnect()

    def create_or_replace_process(self, process_id: int, num_jobs_to_perform: int):
        process = WorkerProcessWrapper(process_id=process_id,
                                       num_jobs_to_perform=num_jobs_to_perform,
                                       device=self.devices[process_id % len(self.devices)],
                                       job_q=self.job_q,
                                       job_update_q=self.job_update_q)
        if len(self.worker_processes) == process.process_id:
            self.worker_processes.append(process)
        elif len(self.worker_processes) > process.process_id:
            self.worker_processes[process_id] = process
        else:
            raise Exception("There is something wrong with the process id!")
