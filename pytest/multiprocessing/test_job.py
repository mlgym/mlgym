from typing import List

import numpy as np
import pytest
import torch
from ml_gym.multiprocessing.job import Job
from ml_gym.util.devices import get_devices

from mocked_func import mocked_sum


class JobFixture:
    @pytest.fixture
    def values(self):
        values = np.arange(0, 100, 1)
        return values

    @pytest.fixture
    def job(self, values):
        job = Job(job_id=0, fun=mocked_sum, param_dict={"arr": values})
        return job

    @pytest.fixture
    def num_jobs(self):
        return 2

    @pytest.fixture
    def jobs(self, num_jobs) -> List[Job]:
        values = np.arange(0, 100, 1)
        jobs = []
        for i in range(num_jobs):
            job = Job(job_id=i, fun=mocked_sum, param_dict={"arr": values})
            jobs.append(job)
        return jobs


class DeviceFixture:
    @pytest.fixture
    def device(self):
        return torch.device(0)

    @pytest.fixture
    def device_ids(self) -> List[int]:
        return [0, 1, 2, 3]

    @pytest.fixture
    def devices(self, device_ids) -> List[torch.device]:
        devices = get_devices(device_ids)
        return devices


class TestJob(JobFixture):

    def test_execute(self, job, values):
        s = job.execute()
        assert s == np.sum(values)

    def test_device(self, job, device):
        assert job.device is None
        job.device = device
        assert job._device == device
