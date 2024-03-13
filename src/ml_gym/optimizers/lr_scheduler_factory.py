from ml_gym.optimizers.lr_schedulers import LRSchedulerAdapter, DummyLRcheduler
from torch.optim.lr_scheduler import LinearLR, ConstantLR, _LRScheduler, LambdaLR
from typing import Dict
from transformers import get_scheduler


class LRSchedulerFactory:
    """
    Learning Rate Scheduler Factory contains different types of available LR Schedulers.
    """
    lr_scheduler_map: Dict[str, _LRScheduler] = {
        "LinearLR": LinearLR,
        "ConstantLR": ConstantLR,
        "LambdaLR": LambdaLR,
        "hugging_face_scheduler": get_scheduler,
        "dummy": DummyLRcheduler

    }

    @classmethod
    def get_lr_scheduler(cls, lr_scheduler_key: str, params: Dict = None) -> LRSchedulerAdapter:
        """
        Get the LRSchedulerAdapter initialzied with the specific Schduler from the lr_scheduler_map.
        :params:
                lr_scheduler_key (str): Scheduler key name from lr_scheduler_map.
                params (dict): Parameters for the LRScheduler.

        :returns:
            Initilzed LRSchedulerAdapter object.
        """
        params = params if params is not None else {}
        lr_scheduler_class = cls.lr_scheduler_map[lr_scheduler_key]
        if lr_scheduler_key == "hugging_face_scheduler":
            if "num_warmup_steps" in params and params["num_warmup_steps"] > 0:
                raise Exception(
                    "The Huggingface learning rate schedulers define the warmup steps in terms of batch steps not epoch steps. This is not compliant to the MLgym implementation and causes issues during training!")
        return LRSchedulerAdapter(lr_scheduler_class=lr_scheduler_class, lr_scheduler_params=params)
