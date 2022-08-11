# import pytest
import glob
import os
import re
from typing import Type, Dict, Any, List

import pytest
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
from ml_gym.util.logger import QueuedLogging
from ml_gym.gym.jobs import AbstractGymJob
from ml_gym.validation.validator_factory import ValidatorFactory

from pytests.test_env.fixtures import LoggingFixture, DeviceFixture
from pytests.test_env.validation_fixtures import ValidationFixtures


class TestGridSearchValidator(LoggingFixture, DeviceFixture, ValidationFixtures):

    @pytest.mark.parametrize("job_type", [AbstractGymJob.Type.STANDARD])
    def test_run(self, blue_print_type: Type[BluePrint], job_type: AbstractGymJob.Type,
                 gs_config: Dict[str, Any], grid_search_id: str, num_epochs: int,
                 dashify_logging_path: str,
                 process_count: int, device_ids: List[int], log_std_to_file: bool, log_dir_path: str,
                 keep_interim_results: bool, start_logging):
        gs_validator = ValidatorFactory.get_gs_validator(grid_search_id=grid_search_id,
                                                         re_eval=False,
                                                         keep_interim_results=keep_interim_results)
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        gs_validator.run(blue_print_type, gym, gs_config, num_epochs, dashify_logging_path)
        QueuedLogging.stop_listener()

        model_paths = glob.glob(os.path.join(dashify_logging_path, grid_search_id, "**/**/**/model_*.pt"))
        assert len(model_paths) != 0
        for model_path in model_paths:
            file_name = os.path.basename(model_path)
            suffix = int(re.findall(r"\d+", file_name)[0])
            assert suffix == num_epochs
