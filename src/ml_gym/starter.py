from typing import List, Type, Dict, Any
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym import Gym
from ml_gym.validation.validator_factory import ValidatorFactory
from datetime import datetime
from ml_gym.util.logger import QueuedLogging
from multiprocessing import Queue
from shutil import copyfile
import os
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.error_handling.exception import ValidationModeNotValidError
from enum import Enum


class MLGymStarter:

    class ValidationMode(Enum):
        NESTED_CV = "nested_cv"
        GRID_SEARCH = "grid_search"

    def __init__(self, blue_print_class: Type[BluePrint], validation_mode: ValidationMode, num_epochs: int, dashify_logging_path: str,
                 gs_config_path: str, evaluation_config_path: str, text_logging_path: str, process_count: int,
                 gpus: List[int], log_std_to_file: bool) -> None:
        self.blue_print_class = blue_print_class
        self.num_epochs = num_epochs
        self.validation_mode = validation_mode
        self.dashify_logging_path = dashify_logging_path
        self.evaluation_config_path = evaluation_config_path
        self.text_logging_path = text_logging_path
        self.process_count = process_count
        self.log_std_to_file = log_std_to_file
        self.gpus = gpus
        self.gs_config_path = gs_config_path

    @staticmethod
    def _create_gym(process_count: int, device_ids, log_std_to_file: bool) -> Gym:
        gym = Gym(process_count, device_ids=device_ids, log_std_to_file=log_std_to_file)
        return gym

    @staticmethod
    def _setup_logging_environment(log_dir_path: str):
        queue = Queue()
        QueuedLogging.start_logging(queue, log_dir_path)

    @staticmethod
    def _stop_logging_environment():
        QueuedLogging.stop_listener()

    @staticmethod
    def _save_gs_config(gs_config_path: str, dashify_logging_path: str, grid_search_id: str):
        gs_logging_path = os.path.join(dashify_logging_path, grid_search_id)
        os.makedirs(gs_logging_path, exist_ok=True)
        copyfile(gs_config_path, os.path.join(gs_logging_path, os.path.basename(gs_config_path)))

    @staticmethod
    def _save_evaluation_config(evaluation_config_path: str, dashify_logging_path: str, grid_search_id: str):
        gs_logging_path = os.path.join(dashify_logging_path, grid_search_id)
        os.makedirs(gs_logging_path, exist_ok=True)
        copyfile(evaluation_config_path, os.path.join(gs_logging_path, os.path.basename(evaluation_config_path)))

    def start(self):
        grid_search_id = datetime.now().strftime("%Y-%m-%d--%H-%M-%S")
        self._save_gs_config(self.gs_config_path, self.dashify_logging_path, grid_search_id)
        self._setup_logging_environment(self.text_logging_path)
        gym = MLGymStarter._create_gym(process_count=self.process_count, device_ids=self.gpus, log_std_to_file=self.log_std_to_file)
        gs_config = YAMLConfigLoader.load(self.gs_config_path)
        if self.validation_mode == MLGymStarter.ValidationMode.NESTED_CV:
            self._save_evaluation_config(self.evaluation_config_path, self.dashify_logging_path, grid_search_id)
            evaluation_config = YAMLConfigLoader.load(self.evaluation_config_path)
            self.run_nested_cv(gym=gym, gs_config=gs_config, cv_config=evaluation_config, grid_search_id=grid_search_id)
        elif self.validation_mode == MLGymStarter.ValidationMode.GRID_SEARCH:
            self.run_grid_search(gym=gym, gs_config=gs_config, grid_search_id=grid_search_id)
        else:
            raise ValidationModeNotValidError
        self._stop_logging_environment()

    def run_nested_cv(self, gym: Gym, cv_config: Dict[str, Any], gs_config: Dict[str, Any], grid_search_id: str):
        nested_cv = ValidatorFactory.get_nested_cv(gs_config=gs_config,
                                                   cv_config=cv_config,
                                                   grid_search_id=grid_search_id,
                                                   blue_print_type=self.blue_print_class)
        nested_cv.run(blue_print_type=self.blue_print_class,
                      gym=gym,
                      gs_config=gs_config,
                      num_epochs=self.num_epochs,
                      dashify_logging_path=self.dashify_logging_path)

    def run_grid_search(self, gym: Gym, gs_config: Dict[str, Any], grid_search_id: str):
        gs_validator = ValidatorFactory.get_gs_validator(grid_search_id=grid_search_id)
        gs_validator.run(blue_print_type=self.blue_print_class,
                         gym=gym,
                         gs_config=gs_config,
                         num_epochs=self.num_epochs,
                         dashify_logging_path=self.dashify_logging_path)
