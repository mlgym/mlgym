from typing import List, Type, Dict, Any
import pytest
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
import torch
from ml_gym.util.logger import QueuedLogging
from ml_gym.validation.validator_factory import ValidatorFactory
from pytests.test_env.fixtures import DeviceFixture, LoggingFixture
from pytests.test_env.validation_fixtures import ValidationFixtures
from ml_gym.modes import RunMode
from pytests.blueprints.constructables.mocked_classes import MockedGridSearchAPIClient, MockedMLgymStatusLogger


torch.multiprocessing.set_start_method('spawn', force=True)


class TestGym(LoggingFixture, DeviceFixture, ValidationFixtures):

    @pytest.fixture
    def gym(self, process_count, device_ids: List[int], log_std_to_file: bool, start_logging):
        mocked_status_logger = MockedMLgymStatusLogger
        gym = Gym(job_id_prefix="xyz_",
                  process_count=process_count,
                  device_ids=device_ids,
                  log_std_to_file=log_std_to_file,
                  logger_collection_constructable=mocked_status_logger)
        return gym

    @pytest.fixture
    def blueprints(self, blue_print_type: Type[BluePrint],
                   gs_cv_config: Dict[str, Any], cv_config: Dict[str, Any],
                   grid_search_id: str,
                   num_epochs: int) -> List[Type[BluePrint]]:
        cross_validator = ValidatorFactory.get_cross_validator(gs_config=gs_cv_config,
                                                               cv_config=cv_config,
                                                               blue_print_type=blue_print_type,
                                                               run_mode=RunMode.TRAIN)
        mocked_status_logger = MockedMLgymStatusLogger
        mocked_gs_api_client = MockedGridSearchAPIClient
        blueprints = cross_validator.create_blue_prints(grid_search_id=grid_search_id,
                                                        blue_print_type=blue_print_type,
                                                        gs_config=gs_cv_config,
                                                        num_epochs=num_epochs,
                                                        logger_collection_constructable=mocked_status_logger,
                                                        gs_api_client_constructable=mocked_gs_api_client)
        return blueprints

    def test_add_blueprints(self, gym: Gym, blueprints: List[Type[BluePrint]]):
        gym.add_blueprints(blueprints)
        assert len(gym.jobs) == len(blueprints)
        for job, blueprint in zip(gym.jobs, blueprints):
            assert job.blueprint == blueprint
        QueuedLogging.stop_listener()

    @pytest.mark.parametrize('parallel', [True, False])
    def test_run(self, gym: Gym, process_count: int, blueprints: List[Type[BluePrint]], parallel: bool):
        gym.add_blueprints(blueprints)
        gym.run(parallel)

        assert True  # TODO come up with a better test

        QueuedLogging.stop_listener()
