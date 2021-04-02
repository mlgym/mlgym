from abc import ABC, abstractmethod
import torch
import torch.nn as nn
from ml_gym.loss_functions.loss_scaler import MeanScaler
from ml_gym.batching.batch import InferenceResultBatch
from typing import List, Callable
from ml_gym.gym.stateful_components import StatefulComponent
import torch.nn.functional as F
from ml_gym.error_handling.exception import InvalidTensorFormatError


class LossWarmupMixin(StatefulComponent):
    def __init__(self):
        self.warmup_loss_tensor: torch.Tensor = torch.Tensor()

    @abstractmethod
    def warm_up(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
        raise NotImplementedError

    @abstractmethod
    def finish_warmup(self):
        raise NotImplementedError


class Loss(ABC):
    def __init__(self, tag: str = ""):
        self._tag = tag

    @property
    def tag(self) -> str:
        return self._tag

    @abstractmethod
    def __call__(self, eval_batch: InferenceResultBatch) -> torch.Tensor:
        """
        Calculates the loss
        :return: Loss tensor
        """
        raise NotImplementedError


class LPLoss(Loss):
    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2,
                 sample_selection_fun: Callable[[InferenceResultBatch], List[bool]] = None,
                 tag: str = "", average_batch_loss: bool = True):
        super().__init__(tag)
        self.root = root
        self.exponent = exponent
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.sample_selection_fun = sample_selection_fun
        self.average_batch_loss = average_batch_loss

    def __call__(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
        # here: predictions are reconstructions and targets are the input vectors
        t = forward_batch.get_targets(self.target_subscription_key)
        p = forward_batch.get_predictions(self.prediction_subscription_key)
        if t.shape != p.shape:
            raise InvalidTensorFormatError

        if self.sample_selection_fun is not None:
            sample_selection_mask = self.sample_selection_fun(forward_batch)
            t = t[sample_selection_mask]
            p = p[sample_selection_mask]
        loss_values = (torch.sum((p - t).abs() ** self.exponent, dim=1) ** (1 / self.root))
        if self.average_batch_loss:
            loss_values = torch.sum(loss_values)/len(loss_values)
        return loss_values


class LPLossScaled(LPLoss):
    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2,
                 sample_selection_fun: Callable[[InferenceResultBatch], List[bool]] = None, tag: str = ""):
        LPLoss.__init__(self, target_subscription_key,
                        prediction_subscription_key, root, exponent, sample_selection_fun, tag)
        self.warmup_losses = []
        # self.scaler = MeanScaler()

    def __call__(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
        loss_tensor = LPLoss.__call__(self, forward_batch)
        # loss_tensor_scaled = self.scaler.scale(loss_tensor)
        return loss_tensor

    # def warm_up(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
    #     # calculate losses
    #     loss_tensor = self(forward_batch)
    #     self.warmup_losses.append(loss_tensor)
    #     return loss_tensor

    # def finish_warmup(self):
    #     loss_tensor = torch.cat(self.warmup_losses)
    #     self.scaler.train(loss_tensor)


class CrossEntropyLoss(Loss):

    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, tag: str = ""):
        super().__init__(tag)
        self.target_subscription_key: str = target_subscription_key
        self.prediction_subscription_key: str = prediction_subscription_key

    def __call__(self, inference_result_batch: InferenceResultBatch) -> torch.Tensor:
        # the targets tensor has each target in a separate tensor torch.Tensor([[1], [2], ..., [1]).
        # For the CrossEntropyLoss API we need them to be squeezed torch.Tensor([1, 2, ..., 1])
        t = inference_result_batch.get_targets(self.target_subscription_key).long()
        p = inference_result_batch.get_predictions(self.prediction_subscription_key)
        loss_values = nn.CrossEntropyLoss(reduction="none")(p, t)
        return loss_values


class NLLLoss(Loss):
    """The negative log likelihood loss.
    NOTE: Obtaining log-probabilities in a neural network is easily achieved by adding a LogSoftmax layer 
    in the last layer of your network. Here, we already did this implicitly in the loss function. 
    Therefore, this loss function is equivalent to CrossEntropyLoss"""

    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, tag: str = ""):
        super().__init__(tag)
        self.target_subscription_key: str = target_subscription_key
        self.prediction_subscription_key: str = prediction_subscription_key

    def __call__(self, inference_result_batch: InferenceResultBatch) -> torch.Tensor:
        t = inference_result_batch.get_targets(self.target_subscription_key).long()
        p = inference_result_batch.get_predictions(self.prediction_subscription_key)
        p = F.log_softmax(p, dim=1)
        loss_values = nn.NLLLoss(reduction="none")(p, t)
        return loss_values


class BCEWithLogitsLoss(Loss):
    def __init__(self, target_subscription_key: str, prediction_subscription_key: str, tag: str = "", average_batch_loss: bool = True):
        super().__init__(tag)
        self.target_subscription_key: str = target_subscription_key
        self.prediction_subscription_key: str = prediction_subscription_key
        self.average_batch_loss = average_batch_loss

    def __call__(self, inference_result_batch: InferenceResultBatch) -> torch.Tensor:
        t = inference_result_batch.get_targets(
            self.target_subscription_key).float().flatten()
        p = inference_result_batch.get_predictions(
            self.prediction_subscription_key).flatten()
        loss_values = nn.BCEWithLogitsLoss(reduction="none")(p, t)
        if self.average_batch_loss:
            loss_values = torch.sum(loss_values)/len(loss_values)
        return loss_values
