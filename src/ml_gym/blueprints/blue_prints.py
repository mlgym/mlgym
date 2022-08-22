from abc import ABC, abstractmethod
from ml_gym.gym.jobs import GymJob
from typing import List, Type, Dict, Any
from ml_gym.modes import RunMode
from ml_gym.persistency.logging import MLgymStatusLoggerCollectionConstructable


class BluePrint(ABC):
    """ Abstract class that provides a blueprint for creating `AbstractGymJob`
    """

    def __init__(self, run_mode: RunMode, epochs: int,
                 config: Dict[str, Any], grid_search_id: str, experiment_id: str,
                 external_injection: Dict[str, Any] = None,
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None):

        self.run_mode = run_mode
        self.config = config
        self.grid_search_id = grid_search_id
        self.experiment_id = experiment_id
        self.epochs = epochs
        self.external_injection = external_injection if external_injection is not None else {}
        self.logger_collection_constructable = logger_collection_constructable

    @abstractmethod
    def construct(self) -> GymJob:
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def construct_components(config: Dict, component_names: List[str], external_injection: Dict[str, Any] = None) -> List[Any]:
        return NotImplementedError

    @staticmethod
    def create_blueprint(blue_print_class: Type["BluePrint"],
                         run_mode: RunMode,
                         experiment_config: Dict[str, Any],
                         experiment_id: str,
                         num_epochs: int,
                         grid_search_id: str,
                         external_injection: Dict[str, Any] = None,
                         logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None) -> List["BluePrint"]:

        blue_print = blue_print_class(grid_search_id=grid_search_id,
                                      experiment_id=experiment_id,
                                      epochs=num_epochs,
                                      run_mode=run_mode,
                                      config=experiment_config,
                                      external_injection=external_injection,
                                      logger_collection_constructable=logger_collection_constructable)
        return blue_print
