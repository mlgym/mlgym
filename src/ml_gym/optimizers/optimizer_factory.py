from torch.optim import Optimizer, SGD, Adam, Adadelta
from functools import partial
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
        optimizer_partial = partial(cls.optimizer_map[optimizer_key], **params)
        return OptimizerAdapter(optimizer_partial=optimizer_partial)
