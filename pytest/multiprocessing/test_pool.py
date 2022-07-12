from multiprocessing import Queue
from typing import List

import pytest
from ml_gym.multiprocessing.job import Job
from ml_gym.multiprocessing.pool import Pool

from ml_gym.util.logger import QueuedLogging

from test_job import JobFixture, DeviceFixture


class TestPool(JobFixture, DeviceFixture):
    @pytest.fixture
    def num_processes(self) -> int:
        return 2

    @pytest.fixture
    def log_std_to_file(self) -> bool:
        return False

    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def pool(self, num_processes, devices, log_dir_path) -> Pool:
        queue = Queue()
        QueuedLogging.start_logging(queue, log_dir_path)
        pool = Pool(num_processes=num_processes, devices=devices)
        return pool

    def test_add_jobs(self, pool: Pool, jobs: List[Job]):
        assert pool.job_q.empty()
        pool.add_jobs(jobs)
        assert not pool.job_q.empty()
        assert pool.job_count == pool.job_q.qsize()
        # remove one by one
        for i in range(pool.job_count):
            pool.job_q.get()
        assert pool.job_q.empty()

    def test_run(self, pool: Pool, jobs: List[Job], num_jobs: int):
        pool.add_jobs(jobs)

        return
