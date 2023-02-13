from dataclasses import dataclass
from typing import Dict, Any
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.batching.batch import InferenceResultBatch
import torch
from torch.nn import CrossEntropyLoss
from ml_gym.blueprints.constructables import LossFunctionRegistryConstructable


@dataclass
class LMLossFunctionRegistryConstructable(LossFunctionRegistryConstructable):
    class LossKeys:
        MLMCrossEntropyLoss = "MLMCrossEntropyLoss"

    def _construct_impl(self):
        loss_fun_registry = super()._construct_impl()
        default_mapping: Dict[str, Any] = {
            self.LossKeys.MLMCrossEntropyLoss: MLMCrossEntropyLoss
        }

        for key, loss_type in default_mapping.items():
            loss_fun_registry.add_class(key, loss_type)

        return loss_fun_registry


class MLMCrossEntropyLoss(Loss):
    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, vocab_size: int,
                 tag: str = ""):
        super().__init__(tag)
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.vocab_size = vocab_size
        self.loss_fun = CrossEntropyLoss()

    def __call__(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
        t = forward_batch.get_targets(self.target_subscription_key)
        p = forward_batch.get_predictions(self.prediction_subscription_key)
        masked_lm_loss = self.loss_fun(p.view(-1, self.vocab_size), t.view(-1))
        return masked_lm_loss
