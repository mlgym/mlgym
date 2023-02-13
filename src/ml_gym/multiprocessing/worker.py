from torch.multiprocessing import Process, Queue
import time
import torch
import traceback
from ml_gym.multiprocessing.job import Job, JobType, JobStatus
from copy import deepcopy


class WorkerProcess(Process):
    def __init__(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, job_update_q: Queue, device: torch.device):
        super(WorkerProcess, self).__init__(target=self.work, args=(job_q, job_update_q, num_jobs_to_perform, device))
        self.process_id = process_id

    def work(self, job_q: Queue, job_update_q: Queue, num_jobs_to_perform: int, device: torch.device):

        jobs_done_count = 0
        for job in iter(job_q.get, None):  # https://stackoverflow.com/a/21157892
            job.status = JobStatus.RUNNING
            job.device = device
            job.executing_process_id = self.process_id
            job.starting_time = time.time()
            job_update_q.put(deepcopy(job))
            if job.job_type == JobType.CALC:
                self._do_calc(job)
            job.finishing_time = time.time()
            job.status = JobStatus.DONE
            jobs_done_count += 1
            job_update_q.put(deepcopy(job))
            if job.job_type == JobType.TERMINATE or num_jobs_to_perform == jobs_done_count:
                break

    def _do_calc(self, job: Job):
        try:
            job.execute()
        except Exception as e:
            job.error = str(e)
            job.stacktrace = traceback.format_exc()


class WorkerProcessWrapper:
    def __init__(self, process_id: int, num_jobs_to_perform: int, device: torch.device, job_q: Queue, job_update_q: Queue):
        self.jobs_done_count = 0
        self.device = device
        self.num_jobs_to_perform = num_jobs_to_perform
        self.process_id = process_id
        self.job_q = job_q
        self.job_update_q = job_update_q
        self.process = WorkerProcess(process_id, num_jobs_to_perform, job_q, job_update_q, device)

    def recreate_process_if_done(self):
        self.jobs_done_count += 1
        if self.num_jobs_to_perform == self.jobs_done_count:
            self.process = WorkerProcess(self.process_id, self.num_jobs_to_perform,
                                         self.job_q, self.job_update_q, self.device, self.logger)
            self.jobs_done_count = 0
            self.process.start()

    def get_process_id(self) -> int:
        return self.process.process_id

    def start(self):
        return self.process.start()
