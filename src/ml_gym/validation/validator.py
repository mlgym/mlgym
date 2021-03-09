from abc import ABC, abstractmethod
from typing import Dict, Any


class ValidatorIF(ABC):

    @abstractmethod
    def run(self, gs_config: Dict[str, Any], num_epochs: int):
        raise NotImplementedError
