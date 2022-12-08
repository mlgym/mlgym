from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.persistency.io import GridSearchAPIClientConstructableIF


class ValidatorIF(ABC):

    @abstractmethod
    def create_blueprints(self, grid_search_id: str, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any],
                          num_epochs: int, dashify_logging_path: str,
                          gs_api_client_constructable: GridSearchAPIClientConstructableIF) -> List[BluePrint]:
        raise NotImplementedError
