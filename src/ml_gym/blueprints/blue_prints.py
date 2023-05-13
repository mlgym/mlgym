from abc import ABC, abstractmethod
from typing import List, Type, Dict, Any
from ml_gym.modes import RunMode
import torch


class BluePrint(ABC):
    """ Abstract class that provides a blueprint for creating all the components for the GymJob`
    """

    def __init__(self, run_mode: RunMode, config: Dict[str, Any], grid_search_id: str,
                 experiment_id: str, external_injection: Dict[str, Any] = None,
                 warm_start_epoch: int = 0):
        """
        Initalize BluePrint class.
        :params:
           - run_mode (RunMode): Create config to run from scratch or do a warm start.
           - config (Dict[str, Any]): This is a dictionary having the configuration keys.
           - grid_search_id (str): Grid Search ID created for the run.
           - experiment_id (str): Experminet Number of the model for which blueprint is created.
           - external_injection (Dict[str, Any]): TO DO
           - warm_start_epoch (int): epoch number to warm start from.
        """ 

        self.run_mode = run_mode
        self.config = config
        self.grid_search_id = grid_search_id
        self.experiment_id = experiment_id
        self.external_injection = external_injection if external_injection is not None else {}
        self.warm_start_epoch = warm_start_epoch

    @abstractmethod
    def construct(self, device: torch.device = None) -> Dict:
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
                         grid_search_id: str,
                         external_injection: Dict[str, Any] = None,
                         warm_start_epoch: int = 0) -> List["BluePrint"]:
        """
        Function to create a blue print Dictionary
        :params:
           - blue_print_class (Type["BluePrint"]): Class call for BluePrint.
           - run_mode (RunMode): Create config to run from scratch or do a warm start.
           - experiment_config (Dict[str, Any]): This is a dictionary having the configuration keys.
           - grid_search_id (str): Grid Search ID created for the run.
           - experiment_id (str): Experminet Number of the model for which blueprint is created.
           - external_injection (Dict[str, Any]): TO DO
           - warm_start_epoch (int): epoch number to warm start from.
        
        :returns: blue_print(List["BluePrint"]) : List of blueprint objects.
        """

        blue_print = blue_print_class(grid_search_id=grid_search_id,
                                      experiment_id=experiment_id,
                                      warm_start_epoch=warm_start_epoch,
                                      run_mode=run_mode,
                                      config=experiment_config,
                                      external_injection=external_injection)
        return blue_print
