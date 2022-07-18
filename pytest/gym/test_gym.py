from typing import List

import pytest
from ml_gym.gym.gym import Gym
import torch

torch.multiprocessing.set_start_method('spawn', force=True)


class TestGym:
    @pytest.fixture
    def process_count(self) -> int:
        return 2

    @pytest.fixture
    def device_ids(self) -> List[int]:
        return [0, 1, 2, 3]

    @pytest.fixture
    def log_std_to_file(self) -> bool:
        return False

    def test_create_gym(self, process_count: int, device_ids, log_std_to_file: bool):
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        return gym
