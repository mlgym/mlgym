import torch
import torch.nn as nn
from abc import abstractmethod


class NNModel(nn.Module):
    def __init__(self, seed: int = None):
        if seed is not None:
            torch.manual_seed(seed)
        super(NNModel, self).__init__()

    @abstractmethod
    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def forward_impl(self, inputs: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError
