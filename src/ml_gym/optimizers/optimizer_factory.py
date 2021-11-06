from torch.optim import Optimizer, SGD, Adam, Adadelta
from typing import Dict
from ml_gym.optimizers.optimizer import OptimizerAdapter


class OptimizerFactory:
    optimizer_map: Dict[str, Optimizer] = {
        "SGD": SGD,
        "ADAM": Adam,
        "ADADELTA": Adadelta
    }

    @classmethod
    def get_optimizer(cls, optimizer_key: str, params: Dict) -> OptimizerAdapter:
        optimizer_class = cls.optimizer_map[optimizer_key]
        return OptimizerAdapter(optimizer_class=optimizer_class, optimizer_params=params)
