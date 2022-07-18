from typing import List

import numpy as np
import pytest
from ml_gym.multiprocessing.job import Job
import torch
from ml_gym.util.devices import get_devices


class JobFixture:
    @pytest.fixture
    def arr(self) -> np.array:
        values = np.arange(0, 100, 1)
        return values

    @pytest.fixture
    def job(self, arr: np.array) -> Job:
        job = Job(job_id=0, fun=mocked_sum, param_dict={"arr": arr})
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
            job = Job(job_id=i, fun=mocked_sum, param_dict={"arr": arrays[i]})
            jobs.append(job)
        return jobs


class DeviceFixture:
    @pytest.fixture
    def device(self) -> torch.device:
        return torch.device(0)

    @pytest.fixture
    def device_ids(self) -> List[int]:
        return [0, 1, 2, 3]

    @pytest.fixture
    def devices(self, device_ids: List[int]) -> List[torch.device]:
        devices = get_devices(device_ids)
        return devices


def mocked_sum(arr, device):
    arr = torch.tensor(np.array(arr), device=device)
    s = 0
    for i in arr:
        s += i
    return s