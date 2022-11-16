from typing import List

import numpy as np
import pytest
import torch
from ml_gym.multiprocessing.job import Job

from pytests.multiprocessing.mocked_func import mocked_sum
from pytests.test_env.fixtures import DeviceFixture


class JobFixture:
    @pytest.fixture
    def arr(self) -> np.array:
        values = np.arange(0, 100, 1)
        return values

    @pytest.fixture
    def job(self, arr: np.array) -> Job:
        job = Job(job_id=0, fun=mocked_sum, param_dict={"arr": arr}, blueprint=None)
        return job

    @pytest.fixture
    def num_jobs(self) -> int:
        return 10

    @pytest.fixture
    def arrays(self, num_jobs: int) -> List[np.array]:
        arrays = []
        for i in range(num_jobs):
            arr = np.random.randint(0, 10, 50)
            arrays.append(arr)
        return arrays

    @pytest.fixture
    def jobs(self, num_jobs: int, arrays: List[np.array]) -> List[Job]:
        jobs = []
        for i in range(num_jobs):
            job = Job(job_id=i, fun=mocked_sum, param_dict={"arr": arrays[i]}, blueprint=None)
            jobs.append(job)
        return jobs


class TestJob(JobFixture, DeviceFixture):

    def test_execute(self, job: Job, arr: np.array):
        s = job.execute()
        assert s == np.sum(arr)
