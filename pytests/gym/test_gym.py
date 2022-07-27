from typing import List

import pytest
from ml_gym.gym.gym import Gym
import torch

from pytests.test_env.fixtures import DeviceFixture
from pytests.test_env.linear_net_blueprint import LinearBluePrint
from pytests.test_env.validation_fixtures import ValidationFixtures

torch.multiprocessing.set_start_method('spawn', force=True)


class TestGym(DeviceFixture, ValidationFixtures):
    @pytest.fixture
    def experiment_id(self) -> int:
        return 0

    @pytest.fixture
    def gym(self, process_count: int = 1, device_ids: List[int] = None, log_std_to_file: bool = True):
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        return gym

    @pytest.fixture
    def test_blue_print(self, device, grid_search_id, experiment_id, num_epochs, run_mode, experiment_config,
                        dashify_logging_path, external_injection, job_type):
        blue_print = LinearBluePrint(grid_search_id=grid_search_id,
                                     run_id=str(experiment_id),
                                     epochs=num_epochs,
                                     run_mode=run_mode,
                                     config=experiment_config,
                                     dashify_logging_dir=dashify_logging_path,
                                     external_injection=external_injection,
                                     job_type=job_type)
        gym_job = blue_print.construct(device)

    def test_add_blue_prints(self, blue_print):
        pass

    def test_run(self):
        # test blueprints
        pass
