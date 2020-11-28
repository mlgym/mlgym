from torch.multiprocessing import Queue
import time
import tqdm
import torch
from typing import List
from ml_gym.multiprocessing.job import JobType, Job
from ml_gym.multiprocessing.worker import WorkerProcessWrapper
from ml_gym.util.logger import QueuedLogging
from ml_gym.util.logger import LogLevel, QLogger


class Pool:
    def __init__(self, num_processes: int, devices: List[torch.device], max_jobs_per_process: int = 1):
        self.num_processes = num_processes
        self._job_count = 0
        self.job_q = Queue()
        self.done_q = Queue()
        self.devices = devices
        self.worker_processes = []
        self.max_jobs_per_process = max_jobs_per_process
        self.logger: QLogger = QueuedLogging.get_qlogger("logger_pool")
        self.logger.log(LogLevel.INFO, f"Initialized to run jobs on: {self.devices}")

    def add_job(self, job: Job):
        self.job_q.put(job)
        self._job_count += 1

    def add_jobs(self, jobs: List[Job]):
        self.logger.log(LogLevel.INFO, "Filling up job queue ... ")
        for job in tqdm.tqdm(jobs):
            self.job_q.put(job)
        self._job_count += len(jobs)

    @property
    def job_count(self):
        return self._job_count

    def run(self):
        jobs_done = 0
        # we have to add the termination jobs at the end of the queue such that the processes stop working and don't get stuck in jobs_q.get()
        termination_jobs = [Job(job_id=-1, fun=None, param_dict=None, job_type=JobType.TERMINATE) for _ in
                            range(self.num_processes)]
        self.add_jobs(termination_jobs)
        # create and start worker processes
        self.logger.log(LogLevel.INFO, f"Creating {self.num_processes} worker processes...")
        for process_id in tqdm.tqdm(range(self.num_processes)):
            self.create_or_replace_process(process_id, self.max_jobs_per_process)
        self.logger.log(LogLevel.INFO, f"Starting {self.num_processes} worker processes...")
        for p in tqdm.tqdm(self.worker_processes):
            p.start()
        # wait until all jobs are done
        for _ in range(self._job_count):
            done_job = self.done_q.get()
            jobs_done += 1
            if done_job.error is not None:
                self.logger.log(LogLevel.FATAL,
                                f"FATAL! Job {done_job.job_id} crashed while being executed by process {done_job.executing_process_id} on {done_job.device} after {int(done_job.finishing_time - done_job.starting_time)} seconds with error {done_job.error}")
                self.logger.log(LogLevel.FATAL, f"Error: {done_job.stacktrace}")
            else:
                self.logger.log(LogLevel.INFO,
                                f"Job {done_job.job_id} was successfully executed by process {done_job.executing_process_id} on {done_job.device} within {int(done_job.finishing_time - done_job.starting_time)} seconds.")
                self.logger.log(LogLevel.INFO, f"Progress: {int(jobs_done / self._job_count * 100)}%")
            if done_job.job_type == JobType.CALC:
                self.worker_processes[done_job.executing_process_id].recreate_process_if_done()

    def create_or_replace_process(self, process_id: int, num_jobs_to_perform: int):
        process = WorkerProcessWrapper(process_id=process_id,
                                       num_jobs_to_perform=num_jobs_to_perform,
                                       device=self.devices[process_id % len(self.devices)],
                                       job_q=self.job_q,
                                       done_q=self.done_q)
        if len(self.worker_processes) == process.process_id:
            self.logger.log(LogLevel.DEBUG, f"Adding process {process_id}.")
            self.worker_processes.append(process)
        elif len(self.worker_processes) > process.process_id:
            self.worker_processes[process_id] = process
            self.logger.log(LogLevel.DEBUG, f"Replaced process {process_id}.")
        else:
            raise Exception("There is something wrong with the process id!")

    if __name__ == "__main__":
        def do_sleep(seconds: int, device: torch.device):
            time.sleep(seconds)
            # print("Device: " + device)
            # raise Exception("bla")

        # pool = Pool(3, max_jobs_per_process=1)
        # pool.add_jobs(jobs)
        # pool.run()
