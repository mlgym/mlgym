from dataclasses import dataclass, field
from abc import abstractmethod
from typing import List, Callable
import torch


@dataclass
class Collator(Callable):

    device: torch.device = field(default_factory=lambda: torch.device("cpu"))

    @abstractmethod
    def __call__(self, batch: List[torch.Tensor]):
        """ Takes a batch and collates into a proper TrainBatch.
        :param batch
        :return:
        """
        raise NotImplementedError
