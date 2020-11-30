from torch.multiprocessing import Process, Queue
import time
import torch
import traceback
from ml_gym.multiprocessing.job import Job, JobType
from ml_gym.util.logger import MLgymLoggerIF, LogLevel, QueuedLogging


class WorkerProcess(Process):
    def __init__(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, done_q: Queue, device: torch.device, logger: MLgymLoggerIF):
        super(WorkerProcess, self).__init__(target=self.work, args=(job_q, done_q, num_jobs_to_perform, device, logger))
        self.process_id = process_id

    def work(self, job_q: Queue, done_q: Queue, num_jobs_to_perform: int, device: torch.device, logger: MLgymLoggerIF):

        logger.log(LogLevel.INFO, f"Process {self.process_id} started working.")
        jobs_done_count = 0
        for job in iter(job_q.get, None):  # https://stackoverflow.com/a/21157892
            job.device = device
            job.executing_process_id = self.process_id
            logger.log(LogLevel.INFO, f"Process {job.executing_process_id} started job {job.job_id} on {job.device}.")
            job.starting_time = time.time()
            if job.job_type == JobType.CALC:
                self._do_calc(job)
            job.finishing_time = time.time()
            job.done = True
            jobs_done_count += 1
            if job.job_type == JobType.TERMINATE or num_jobs_to_perform == jobs_done_count:
                logger.log(LogLevel.DEBUG, f"Process {self.process_id} terminated.")
                done_q.put(job)
                break

    def _do_calc(self, job: Job):
        try:
            job.execute()
        except Exception as e:
            job.error = str(e)
            job.stacktrace = traceback.format_exc()


class WorkerProcessWrapper:
    def __init__(self, process_id: int, num_jobs_to_perform: int, device: torch.device, job_q: Queue, done_q: Queue):
        self.logger = QueuedLogging.get_qlogger(f"logger_process_{process_id}", )
        self.jobs_done_count = 0
        self.device = device
        self.num_jobs_to_perform = num_jobs_to_perform
        self.process_id = process_id
        self.job_q = job_q
        self.done_q = done_q
        self.process = WorkerProcess(process_id, num_jobs_to_perform, job_q, done_q, device, self.logger)

    def recreate_process_if_done(self):
        self.jobs_done_count += 1
        if self.num_jobs_to_perform == self.jobs_done_count:
            self.logger.log(LogLevel.DEBUG, f"Recreating process {self.process_id}.")
            self.process = WorkerProcess(self.process_id, self.num_jobs_to_perform,
                                         self.job_q, self.done_q, self.device, self.logger)
            self.process.start()
            self.logger.log(LogLevel.DEBUG, f"Recreated process {self.process_id}.")
            self.jobs_done_count = 0

    def get_process_id(self) -> int:
        return self.process.process_id

    def start(self):
        return self.process.start()
