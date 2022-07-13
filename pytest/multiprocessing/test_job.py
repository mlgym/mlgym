from multiprocessing import Queue
from typing import List, Tuple

import numpy as np
import pytest
import torch
from ml_gym.multiprocessing.job import Job
from ml_gym.util.devices import get_devices
from ml_gym.util.logger import QueuedLogging

from mocked_func import mocked_sum


class JobFixture:
    @pytest.fixture
    def arr(self):
        values = np.arange(0, 100, 1)
        return values

    @pytest.fixture
    def job(self, arr):
        job = Job(job_id=0, fun=mocked_sum, param_dict={"arr": arr})
        return job

    @pytest.fixture
    def num_jobs(self):
        return 10

    @pytest.fixture
    def arrays(self, num_jobs):
        arrays = []
        for i in range(num_jobs):
            arr = np.random.randint(0, 10, 50)
            arrays.append(arr)
        return arrays

    @pytest.fixture
    def jobs(self, num_jobs, arrays) -> List[Job]:
        jobs = []
        for i in range(num_jobs):
            job = Job(job_id=i, fun=mocked_sum, param_dict={"arr": arrays[i]})
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


class LoggingFixture:
    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def start_logging(self, log_dir_path):
        if QueuedLogging._instance is None:
            queue = Queue()
            QueuedLogging.start_logging(queue, log_dir_path)



class TestJob(JobFixture, DeviceFixture):

    def test_execute(self, job, arr):
        s = job.execute()
        assert s == np.sum(arr)

    def test_device(self, job, device):
        assert job.device is None
        job.device = device
        assert job._device == device
