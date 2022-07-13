from typing import List

import numpy as np
import pytest
from ml_gym.multiprocessing.job import JobType, Job
from ml_gym.multiprocessing.worker import WorkerProcessWrapper, WorkerProcess
from ml_gym.util.logger import QueuedLogging
from multiprocessing import Queue
import torch

from test_job import JobFixture, DeviceFixture, LoggingFixture


class TestWorkerProcess(JobFixture, DeviceFixture, LoggingFixture):
    @pytest.fixture
    def process_id(self) -> int:
        return 0

    @pytest.fixture
    def num_jobs_to_perform(self) -> int:
        return 1

    @pytest.fixture
    def job_q(self, jobs):
        job_q = Queue()
        for job in jobs:
            job_q.put(job)
        termination_job = Job(job_id=-1, fun=None, param_dict=None, job_type=JobType.TERMINATE)
        job_q.put(termination_job)
        return job_q

    @pytest.fixture
    def done_q(self):
        done_q = Queue()
        return done_q

    def test_work_process(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, done_q: Queue,
                          arrays: np.array, device: torch.device, start_logging):
        logger = QueuedLogging.get_qlogger(f"logger_process_{process_id}")

        process = WorkerProcess(process_id, num_jobs_to_perform, job_q, done_q, device, logger)
        assert done_q.qsize() == 0
        process.start()
        # wait until num_jobs_to_perform jobs done in job_q
        done_job = done_q.get()
        assert done_job.done and done_job.job_type == JobType.CALC and done_job.job_id == num_jobs_to_perform - 1

    def test_work_process_wrapper(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, done_q: Queue,
                                  devices: List[torch.device], start_logging):
        process = WorkerProcessWrapper(process_id=process_id,
                                       num_jobs_to_perform=num_jobs_to_perform,
                                       device=devices[process_id % len(devices)],
                                       job_q=job_q,
                                       done_q=done_q)
        process.start()
        # wait until num_jobs_to_perform jobs done in job_q
        done_job = done_q.get()
        assert done_job.done and done_job.job_type == JobType.CALC and done_job.job_id == num_jobs_to_perform - 1
        return process

    def test_recreate_process_if_done(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, done_q: Queue,
                                      devices: List[torch.device], start_logging):
        process = WorkerProcessWrapper(process_id=process_id,
                                       num_jobs_to_perform=num_jobs_to_perform,
                                       device=devices[process_id % len(devices)],
                                       job_q=job_q,
                                       done_q=done_q)
        process.start()
        old_process_id = process.get_process_id()
        # wait until num_jobs_to_perform jobs done in job_q
        done_q.get()
        # recreate the process if this process has already done #num_jobs_to_perform jobs
        process.recreate_process_if_done()
        # wait until num_jobs_to_perform jobs done in job_q
        done_job = done_q.get()
        assert done_job.done and done_job.job_type == JobType.CALC and done_job.job_id == 2 * num_jobs_to_perform - 1
        assert old_process_id == process.get_process_id()
