from typing import List

import pytest
from ml_gym.gym.gym import Gym
import torch

from example.conv_net_blueprint import ConvNetBluePrint
from pytests.test_env.fixtures import DeviceFixture

torch.multiprocessing.set_start_method('spawn', force=True)


class TestGym(DeviceFixture, ):

    @pytest.fixture
    def blue_print(self, device):
        blue_print = ConvNetBluePrint(grid_search_id=grid_search_id,
                                      run_id=str(experiment_id),
                                      epochs=num_epochs,
                                      run_mode=run_mode,
                                      config=experiment_config,
                                      dashify_logging_dir=dashify_logging_path,
                                      external_injection=external_injection,
                                      job_type=job_type)
        blue_print.construct(device)
        pass

    def test_create_gym(self, process_count: int, device_ids, log_std_to_file: bool):
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        return gym

    def test_add_blue_prints(self):
        pass

    def test_run(self):
        # test blueprints
        pass
