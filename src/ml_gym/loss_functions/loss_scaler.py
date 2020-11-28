from abc import abstractmethod
import torch
from ml_gym.gym.stateful_components import StatefulComponent
from typing import Dict, Any


class Scaler(StatefulComponent):

    @abstractmethod
    def train(self, loss: torch.Tensor):
        raise NotImplementedError

    @abstractmethod
    def scale(self, tensor: torch.Tensor) -> torch.Tensor:
        raise NotImplementedError


class MeanScaler(Scaler):
    def __init__(self):
        self._mean = 1

    @property
    def mean(self) -> float:
        return self._mean

    @mean.setter
    def mean(self, value: float):
        self._mean = value

    def scale(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor / self._mean

    def train(self, loss: torch.Tensor):
        self._mean = torch.mean(loss).item()

    def get_state(self) -> Dict[str, Any]:
        state = super().get_state()
        state["mean"] = self.mean
        return state

    def set_state(self, state: Dict[str, Any]):
        super().set_state(state)
        self._mean = state["mean"]


class NoScaler(Scaler):
    def __init__(self):
        pass

    def scale(self, tensor: torch.Tensor) -> torch.Tensor:
        return tensor

    def train(self, loss: torch.Tensor):
        pass
