import glob
import os
import re
from typing import  List

import pytest
from ml_gym.starter import MLGymStarter

from pytests.test_env.fixtures import LoggingFixture, DeviceFixture
from pytests.test_env.validation_fixtures import ValidationFixtures


class TestGymStarter(LoggingFixture, DeviceFixture, ValidationFixtures):

    @pytest.fixture
    def dashify_logging_path(self):
        return "dashify_logging"

    @pytest.fixture
    def text_logging_path(self):
        return "general_logging"

    @pytest.fixture
    def gpus(self):
        return [0]

    @pytest.mark.parametrize("validation_mode", [(MLGymStarter.ValidationMode.GRID_SEARCH)])
    def test_gs_starter(self, blue_print_type,
                        validation_mode,
                        num_epochs: int,
                        dashify_logging_path: str,
                        gs_config_path: str,
                        text_logging_path: str,
                        cv_config_path: str,
                        process_count: int,
                        gpus: List[int],
                        log_std_to_file: bool,
                        grid_search_id: str,
                        keep_interim_results: bool):
        starter = MLGymStarter(blue_print_class=blue_print_type,
                               validation_mode=validation_mode,
                               dashify_logging_path=dashify_logging_path,
                               text_logging_path=text_logging_path,
                               process_count=process_count,
                               gpus=gpus,
                               log_std_to_file=log_std_to_file,
                               gs_config_path=gs_config_path,
                               evaluation_config_path=cv_config_path,
                               num_epochs=num_epochs,
                               keep_interim_results=keep_interim_results)
        starter.start()

        model_paths = glob.glob(os.path.join(dashify_logging_path, grid_search_id, "**/**/**/model_*.pt"))
        assert len(model_paths) != 0

        for model_path in model_paths:
            file_name = os.path.basename(model_path)
            suffix = int(re.findall(r"\d+", file_name)[0])
            assert suffix == num_epochs
        starter._stop_logging_environment()

    @pytest.mark.parametrize("validation_mode", [(MLGymStarter.ValidationMode.CROSS_VALIDATION)])
    def test_cv_starter(self, blue_print_type,
                        validation_mode,
                        num_epochs: int,
                        dashify_logging_path: str,
                        gs_cv_config_path: str,
                        text_logging_path: str,
                        cv_config_path: str,
                        process_count: int,
                        gpus: List[int],
                        log_std_to_file: bool,
                        grid_search_id: str,
                        keep_interim_results: bool):
        starter = MLGymStarter(blue_print_class=blue_print_type,
                               validation_mode=validation_mode,
                               dashify_logging_path=dashify_logging_path,
                               text_logging_path=text_logging_path,
                               process_count=process_count,
                               gpus=gpus,
                               log_std_to_file=log_std_to_file,
                               gs_config_path=gs_cv_config_path,
                               evaluation_config_path=cv_config_path,
                               num_epochs=num_epochs,
                               keep_interim_results=keep_interim_results)
        starter.start()

        model_paths = glob.glob(os.path.join(dashify_logging_path, grid_search_id, "**/**/**/model_*.pt"))
        assert len(model_paths) != 0

        for model_path in model_paths:
            file_name = os.path.basename(model_path)
            suffix = int(re.findall(r"\d+", file_name)[0])
            assert suffix == num_epochs
        starter._stop_logging_environment()
