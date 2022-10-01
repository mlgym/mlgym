from torch.multiprocessing import Queue
import tqdm
import torch
from typing import List
from ml_gym.multiprocessing.job import JobType, Job, JobCollection, JobStatusSubscriberIF
from ml_gym.multiprocessing.worker import WorkerProcessWrapper
from ml_gym.util.logger import QueuedLogging
from ml_gym.util.logger import LogLevel, QLogger
from ml_gym.multiprocessing.job import JobStatus
from ml_gym.persistency.logging import JobStatusLogger, MLgymStatusLoggerCollectionConstructable


class JobStatusLoggingSubscriber(JobStatusSubscriberIF):

    def __init__(self, logger: JobStatusLogger):
        self._logger = logger

    def callback_job_event(self, job: Job):
        representation = {"job_id": job.job_id, "job_type": job.job_type, "grid_search_id": job.grid_search_id, "experiment_id": job.experiment_id, "status": job.status,
                          "starting_time": job.starting_time, "finishing_time": job.finishing_time, "error": job.error,
                          "stacktrace": job.stacktrace, "device": job.device}
        self._logger.log_job_status(**representation)


class Pool:
    def __init__(self, num_processes: int, devices: List[torch.device], max_jobs_per_process: int = 1,
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None):
        self.num_processes = num_processes
        self.job_q = Queue()
        self.job_update_q = Queue()
        self.devices = devices
        self.worker_processes = []
        self.max_jobs_per_process = max_jobs_per_process
        self.logger: QLogger = QueuedLogging.get_qlogger("logger_pool")
        self.logger.log(LogLevel.INFO, f"Initialized to run jobs on: {self.devices}")
        self.job_collection = JobCollection()
        if logger_collection_constructable is not None:
            logger_collection = logger_collection_constructable.construct()
            job_status_logger = JobStatusLogger(logger=logger_collection)
            subscriber = JobStatusLoggingSubscriber(job_status_logger)
            self.job_collection.add_subscriber(subscriber)

    def add_job(self, job: Job):
        self.job_q.put(job)
        self.job_collection.add_or_update_job(job)

    def add_jobs(self, jobs: List[Job]):
        self.logger.log(LogLevel.INFO, "Filling up job queue ... ")
        for job in tqdm.tqdm(jobs):
            self.job_q.put(job)
            self.job_collection.add_or_update_job(job)

    def run(self):
        # we have to add the termination jobs at the end of the queue such that the processes stop working and don't get stuck in jobs_q.get()
        termination_jobs = [Job(job_id=i+len(self.job_collection), fun=None, blueprint=None, param_dict=None,
                                job_type=JobType.TERMINATE) for i in range(self.num_processes)]
        self.add_jobs(termination_jobs)
        # create and start worker processes
        self.logger.log(LogLevel.INFO, f"Creating {self.num_processes} worker processes...")
        for process_id in tqdm.tqdm(range(self.num_processes)):
            self.create_or_replace_process(process_id, self.max_jobs_per_process)
        self.logger.log(LogLevel.INFO, f"Starting {self.num_processes} worker processes...")
        for p in tqdm.tqdm(self.worker_processes):
            p.start()
        # wait until all jobs are done
        while not self.job_collection.done:
            updated_job: Job = self.job_update_q.get()
            self.job_collection.add_or_update_job(updated_job)
            if updated_job.status == JobStatus.DONE and updated_job.error is not None:
                self.logger.log(
                    LogLevel.FATAL, f"FATAL! Job {updated_job.job_id} crashed while being executed by process {updated_job.executing_process_id} on {updated_job.device} after {int(updated_job.finishing_time - updated_job.starting_time)} seconds with error {updated_job.error}")
                self.logger.log(LogLevel.FATAL, f"Error: {updated_job.stacktrace}")
            elif updated_job.status == JobStatus.DONE:
                self.logger.log(
                    LogLevel.INFO, f"Job {updated_job.job_id} was successfully executed by process {updated_job.executing_process_id} on {updated_job.device} within {int(updated_job.finishing_time - updated_job.starting_time)} seconds.")
                self.logger.log(LogLevel.INFO, f"Progress: {int(self.job_collection.done_count / self.job_collection.job_count * 100)}%")
            if updated_job.status == JobStatus.DONE and updated_job.job_type == JobType.CALC:
                self.worker_processes[updated_job.executing_process_id].recreate_process_if_done()

    def create_or_replace_process(self, process_id: int, num_jobs_to_perform: int):
        process = WorkerProcessWrapper(process_id=process_id,
                                       num_jobs_to_perform=num_jobs_to_perform,
                                       device=self.devices[process_id % len(self.devices)],
                                       job_q=self.job_q,
                                       job_update_q=self.job_update_q)
        if len(self.worker_processes) == process.process_id:
            self.logger.log(LogLevel.DEBUG, f"Adding process {process_id}.")
            self.worker_processes.append(process)
        elif len(self.worker_processes) > process.process_id:
            self.worker_processes[process_id] = process
            self.logger.log(LogLevel.DEBUG, f"Replaced process {process_id}.")
        else:
            raise Exception("There is something wrong with the process id!")

