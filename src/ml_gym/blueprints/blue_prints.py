from abc import ABC, abstractmethod
from ml_gym.gym.jobs import GymJob
from typing import List, Type, Dict, Any
from ml_gym.modes import RunMode
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable
import torch
from ml_gym.persistency.io import GridSearchAPIClientConstructableIF


class BluePrint(ABC):
    """ Abstract class that provides a blueprint for creating `AbstractGymJob`
    """

    def __init__(self, run_mode: RunMode, num_epochs: int,
                 config: Dict[str, Any], grid_search_id: str,
                 gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                 experiment_id: str,
                 external_injection: Dict[str, Any] = None,
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None,
                 warm_start_epoch: int = 0):

        self.run_mode = run_mode
        self.config = config
        self.grid_search_id = grid_search_id
        self.experiment_id = experiment_id
        self.num_epochs = num_epochs
        self.external_injection = external_injection if external_injection is not None else {}
        self.logger_collection_constructable = logger_collection_constructable
        self.warm_start_epoch = warm_start_epoch
        self.gs_api_client_constructable = gs_api_client_constructable

    @abstractmethod
    def construct(self, device: torch.device = None) -> GymJob:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def construct_components(config: Dict, component_names: List[str], device: torch.device,
                             external_injection: Dict[str, Any] = None) -> List[Any]:
        return NotImplementedError

    @staticmethod
    def create_blueprint(blue_print_class: Type["BluePrint"],
                         run_mode: RunMode,
                         experiment_config: Dict[str, Any],
                         experiment_id: str,
                         num_epochs: int,
                         grid_search_id: str,
                         gs_api_client_constructable: GridSearchAPIClientConstructableIF,
                         external_injection: Dict[str, Any] = None,
                         logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None,
                         warm_start_epoch: int = 0) -> List["BluePrint"]:

        blue_print = blue_print_class(grid_search_id=grid_search_id,
                                      experiment_id=experiment_id,
                                      num_epochs=num_epochs,
                                      warm_start_epoch=warm_start_epoch,
                                      run_mode=run_mode,
                                      config=experiment_config,
                                      external_injection=external_injection,
                                      logger_collection_constructable=logger_collection_constructable,
                                      gs_api_client_constructable=gs_api_client_constructable)
        return blue_print
