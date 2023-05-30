from torch.optim import Optimizer, SGD, Adam, Adadelta, AdamW
from typing import Dict
from ml_gym.optimizers.optimizer import OptimizerAdapter


class OptimizerFactory:
    """
    Optimizer Factory contains different types of available Optimizer functions.
    """
    optimizer_map: Dict[str, Optimizer] = {
        "SGD": SGD,
        "ADAM": Adam,
        "ADADELTA": Adadelta,
        "ADAMW": AdamW
    }

    @classmethod
    def get_optimizer(cls, optimizer_key: str, params: Dict) -> OptimizerAdapter:
        """
        Get the OptimizerAdapter initialzied with the specific optimizer from the optimizer_map.
        :params:
            - optimizer_key (str): Scheduler key name from lr_scheduler_map.
            - params (dict): Optimizer parameters.

        :returns:
            Initilzed OptimizerAdapter object.
        """
        optimizer_class = cls.optimizer_map[optimizer_key]
        return OptimizerAdapter(optimizer_class=optimizer_class, optimizer_params=params)
