from multiprocessing import Queue

import pytest
import torch
from typing import List

from ml_gym.util.devices import get_devices
from ml_gym.util.logger import QueuedLogging


class DeviceFixture:
    @pytest.fixture
    def device(self) -> torch.device:
        return torch.device(0)

    @pytest.fixture
    def device_ids(self) -> List[int]:
        return [0]

    @pytest.fixture
    def devices(self, device_ids: List[int]) -> List[torch.device]:
        devices = get_devices(device_ids)
        return devices


class LoggingFixture:
    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def start_logging(self, log_dir_path: str):
        if QueuedLogging._instance is None:
            queue = Queue()
            QueuedLogging.start_logging(queue, log_dir_path)
