from dataclasses import dataclass
from abc import ABC, abstractmethod
from typing import List
import torch


@dataclass
class CollatorIF(ABC):

    @abstractmethod
    def __call__(self, batch: List[torch.Tensor]):
        """ Takes a batch and collates into a proper TrainBatch.
        :param batch
        :return:
        """
        raise NotImplementedError
