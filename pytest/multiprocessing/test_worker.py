from typing import List

import pytest
from ml_gym.multiprocessing.job import JobType, Job
from ml_gym.multiprocessing.worker import WorkerProcessWrapper, WorkerProcess
from ml_gym.util.logger import MLgymLoggerIF, QueuedLogging
from multiprocessing import Queue
import torch

from test_job import JobFixture, DeviceFixture


class TestWorkerProcess(JobFixture, DeviceFixture):
    @pytest.fixture
    def process_id(self) -> int:
        return 0

    @pytest.fixture
    def num_jobs_to_perform(self) -> int:
        return 2

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

    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def logger(self, process_id, log_dir_path):
        queue = Queue()
        QueuedLogging.start_logging(queue, log_dir_path)
        logger = QueuedLogging.get_qlogger(f"logger_process_{process_id}", )
        return logger

    def test_work_process(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, done_q: Queue,
                          device: torch.device, logger: MLgymLoggerIF):
        job_q_size = job_q.qsize()
        process = WorkerProcess(process_id, num_jobs_to_perform, job_q, done_q, device, logger)
        assert done_q.qsize() == 0
        process.start()
        # wait until all job in job_q done
        for _ in range(job_q_size):
            done_job = done_q.get()
            assert done_job.done
            if done_job.done:
                break

    def test_work_process_wrapper(self, process_id: int, num_jobs_to_perform: int, job_q: Queue, done_q: Queue,
                                  devices: List[torch.device], logger: MLgymLoggerIF):
        process = WorkerProcessWrapper(process_id=process_id,
                                       num_jobs_to_perform=num_jobs_to_perform,
                                       device=devices[process_id % len(devices)],
                                       job_q=job_q,
                                       done_q=done_q)
        return process
