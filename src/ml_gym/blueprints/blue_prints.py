from abc import ABC, abstractmethod
from ml_gym.gym.jobs import GymJob
from dashify.logging.dashify_logging import DashifyLogger, ExperimentInfo
from ml_gym.gym.jobs import AbstractGymJob
from typing import List, Type, Dict, Any


class BluePrint(ABC):
    """ Abstract class that provides a blueprint for creating `AbstractGymJob`
    """

    def __init__(self, run_mode: AbstractGymJob.Mode, job_type: AbstractGymJob.Type, model_name: str, dataset_name: str,  epochs: int,
                 config: Dict[str, Any], dashify_logging_dir: str,
                 grid_search_id: str, run_id: str, external_injection: Dict[str, Any] = None):

        self.run_mode = run_mode
        self.job_type = job_type
        self.config = config
        self.dashify_logging_dir = dashify_logging_dir
        self.grid_search_id = grid_search_id
        self.run_id = run_id
        self.epochs = epochs
        self.model_name = model_name
        self.dataset_name = dataset_name
        self.external_injection = external_injection if external_injection is not None else {}

    @abstractmethod
    def construct(self) -> GymJob:
        raise NotImplementedError

    def get_experiment_info(self) -> ExperimentInfo:
        experiment_info = DashifyLogger.create_new_experiment(log_dir=self.dashify_logging_dir,
                                                              subfolder_id=self.grid_search_id,
                                                              model_name=self.model_name,
                                                              dataset_name=self.dataset_name,
                                                              run_id=self.run_id)
        DashifyLogger.save_config(config=self.config, experiment_info=experiment_info)
        return experiment_info

    @staticmethod
    @abstractmethod
    def construct_components(config: Dict, component_names: List[str], external_injection: Dict[str, Any] = None) -> List[Any]:
        return NotImplementedError


def create_blueprint(blue_print_class: Type[BluePrint],
                     run_mode: AbstractGymJob.Mode,
                     job_type: AbstractGymJob.Type,
                     experiment_config: Dict[str, Any],
                     experiment_id: int,
                     dashify_logging_path: str,
                     num_epochs: int,
                     grid_search_id: str,
                     external_injection: Dict[str, Any] = None) -> List[BluePrint]:

    blue_print = blue_print_class(grid_search_id=grid_search_id,
                                  run_id=str(experiment_id),
                                  epochs=num_epochs,
                                  run_mode=run_mode,
                                  config=experiment_config,
                                  dashify_logging_dir=dashify_logging_path,
                                  external_injection=external_injection,
                                  job_type=job_type)
    return blue_print
