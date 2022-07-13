from typing import List

import pytest
from ml_gym.multiprocessing.job import Job
from ml_gym.multiprocessing.pool import Pool

from test_job import JobFixture, DeviceFixture, LoggingFixture


class TestPool(JobFixture, DeviceFixture, LoggingFixture):
    @pytest.fixture
    def num_processes(self) -> int:
        return 2

    @pytest.fixture
    def log_std_to_file(self) -> bool:
        return False

    @pytest.fixture
    def pool(self, num_processes, devices, start_logging) -> Pool:
        pool = Pool(num_processes=num_processes, devices=devices)
        return pool

    def test_add_jobs(self, pool: Pool, jobs: List[Job]):
        assert pool.job_q.empty()
        pool.add_jobs(jobs)
        assert not pool.job_q.empty() and pool.job_count == pool.job_q.qsize()
        # remove one by one
        for i in range(pool.job_count):
            pool.job_q.get()
        assert pool.job_q.empty()

    def test_run(self, pool: Pool, jobs: List[Job], num_processes: int):
        pool.add_jobs(jobs)
        assert pool.job_q.qsize() == 10
        pool.run()
        assert pool.job_q.qsize() == 0
        assert pool.done_q.qsize() == 0
        assert len(pool.worker_processes) == num_processes