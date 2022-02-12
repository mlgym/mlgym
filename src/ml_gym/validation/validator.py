from abc import ABC, abstractmethod
from typing import Dict, Any, Type, List
from ml_gym.blueprints.blue_prints import BluePrint


class ValidatorIF(ABC):

    @abstractmethod
    def create_blueprints(self, blue_print_type: Type[BluePrint], gs_config: Dict[str, Any],
                          num_epochs: int, dashify_logging_path: str) -> List[BluePrint]:
        raise NotImplementedError
