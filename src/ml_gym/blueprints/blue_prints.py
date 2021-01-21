from abc import ABC, abstractmethod
from typing import Dict, Any, List
from ml_gym.gym.jobs import GymJob
from dashify.logging.dashify_logging import DashifyLogger, ExperimentInfo


class BluePrint(ABC):
    """ Abstract class that provides a blueprint for creating `AbstractGymJob`
    """

    def __init__(self, model_name: str, dataset_name: str,  epochs: List[int], config: Dict[str, Any], dashify_logging_dir: str, grid_search_id: str, run_id: str):

        self.config = config
        self.dashify_logging_dir = dashify_logging_dir
        self.grid_search_id = grid_search_id
        self.run_id = run_id
        self.epochs = epochs
        self.model_name = model_name
        self.dataset_name = dataset_name

    @abstractmethod
    def construct(self) -> GymJob:
        raise NotImplementedError

    def get_experiment_info(self, log_dir: str, grid_search_id: str, model_name: str, dataset_name: str, run_id: str) -> ExperimentInfo:
        experiment_info = DashifyLogger.create_new_experiment(log_dir=self.dashify_logging_dir,
                                                              subfolder_id=self.grid_search_id,
                                                              model_name=self.model_name,
                                                              dataset_name=self.dataset_name,
                                                              run_id=self.run_id)
        DashifyLogger.save_config(config=self.config, experiment_info=experiment_info)
        return experiment_info

    @staticmethod
    @abstractmethod
    def construct_components(config: Dict) -> List[Any]:
        return NotImplementedError
