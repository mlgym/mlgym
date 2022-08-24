from typing import List, Type, Dict, Any

import pytest
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
import torch
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.util.logger import QueuedLogging
from ml_gym.validation.validator_factory import ValidatorFactory

from pytests.test_env.fixtures import DeviceFixture, LoggingFixture
from pytests.test_env.validation_fixtures import ValidationFixtures

torch.multiprocessing.set_start_method('spawn', force=True)


class TestGym(LoggingFixture, DeviceFixture, ValidationFixtures):

    @pytest.fixture
    def gym(self, process_count, device_ids: List[int], log_std_to_file: bool, start_logging):
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        return gym

    @pytest.fixture
    def job_type(self):
        return AbstractGymJob.Type.STANDARD

    @pytest.fixture
    def blueprints(self, blue_print_type: Type[BluePrint],
                   job_type: AbstractGymJob.Type, gs_cv_config: Dict[str, Any], cv_config: Dict[str, Any],
                   grid_search_id: str, num_epochs: int,
                   dashify_logging_path: str,
                   keep_interim_results: bool) -> List[Type[BluePrint]]:
        cross_validator = ValidatorFactory.get_cross_validator(gs_config=gs_cv_config,
                                                               cv_config=cv_config,
                                                               grid_search_id=grid_search_id,
                                                               blue_print_type=blue_print_type,
                                                               re_eval=False,
                                                               keep_interim_results=keep_interim_results)
        blueprints = cross_validator.create_blue_prints(blue_print_type=blue_print_type,
                                                        gs_config=gs_cv_config,
                                                        dashify_logging_path=dashify_logging_path,
                                                        num_epochs=num_epochs,
                                                        job_type=job_type)
        return blueprints

    def test_add_blueprints(self, gym: Gym, blueprints: List[Type[BluePrint]]):
        gym.add_blue_prints(blueprints)
        assert len(gym.jobs) == len(blueprints)
        for job, blueprint in zip(gym.jobs, blueprints):
            assert job.param_dict["blue_print"] == blueprint
        QueuedLogging.stop_listener()

    @pytest.mark.parametrize('parallel', [True, False])
    def test_run(self, gym, process_count, blueprints, parallel):
        gym.add_blue_prints(blueprints)
        gym.run(parallel)

        if parallel:
            assert gym.pool._job_count == len(blueprints) + process_count
        else:
            assert gym.pool._job_count == 0

        QueuedLogging.stop_listener()

