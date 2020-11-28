from torch.optim import Optimizer, SGD, Adam, Adadelta
from functools import partial
from typing import Dict


class OptimizerFactory:
    optimizer_map: Dict[str, Optimizer] = {
        "SGD": SGD,
        "ADAM": Adam,
        "ADADELTA": Adadelta
    }

    @classmethod
    def get_partial_optimizer(cls, optimizer_key: str, params: Dict):
        return partial(cls.optimizer_map[optimizer_key], **params)
