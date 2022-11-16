import os
import tempfile
import pytest
import torch
from typing import List
from ml_gym.util.devices import get_devices
from ml_gym.util.logger import QueuedLogging
from ml_gym.error_handling.exception import SingletonAlreadyInstantiatedError


class DeviceFixture:
    @pytest.fixture
    def device(self) -> torch.device:
        device = get_devices([0])[0]

        return device

    @pytest.fixture
    def device_ids(self) -> List[int]:
        return [0]

    @pytest.fixture
    def devices(self, device_ids: List[int]) -> List[torch.device]:
        devices = get_devices(device_ids)
        return devices


class LoggingFixture:

    @pytest.fixture
    def start_logging(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_dir_path = os.path.join(tmp, 'mlgym_logging')
            try:
                QueuedLogging.start_logging(log_dir_path)
            except SingletonAlreadyInstantiatedError:
                pass
