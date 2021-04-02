from typing import List
from ml_gym.loss_functions.loss_functions import Loss, LossWarmupMixin
from ml_gym.loss_functions.loss_scaler import Scaler
from ml_gym.batching.batch import InferenceResultBatch
import torch


class MultiLoss(LossWarmupMixin, Loss):
    def __init__(self, tag: str, scalers: List[Scaler],
                 loss_terms: List[Loss], loss_weights: List[float]):
        LossWarmupMixin.__init__(self)
        Loss.__init__(self, tag)
        self.loss_terms = loss_terms
        self.scalers = scalers
        self.loss_weights = loss_weights
        self.warmup_losses = []

    # def warm_up(self, forward_batch: InferenceResultBatch) -> torch.Tensor:
    #     loss_tensors = self._calc_loss(forward_batch)
    #     self.warmup_losses.append(loss_tensors)
    #     for loss_term in self.loss_terms:
    #         if isinstance(loss_term, LossWarmupMixin):
    #             loss_term.warm_up(forward_batch)
    #     return torch.cat(loss_tensors).sum()

    # def finish_warmup(self):
    #     combined_batch_warmup_losses = [torch.cat(loss_term_loss) for loss_term_loss in zip(*self.warmup_losses)]
    #     for i in range(len(self.loss_terms)):
    #         self.scalers[i].train(combined_batch_warmup_losses[i])

    #     for loss_term in self.loss_terms:
    #         if isinstance(loss_term, LossWarmupMixin):
    #             loss_term.finish_warmup()

    def _scale(self, loss_tensors: List[torch.Tensor]) -> List[torch.Tensor]:
        return [self.scalers[i].scale(tensor) for i, tensor in enumerate(loss_tensors)]

    def _apply_loss_weights(self, loss_tensors: List[torch.Tensor]) -> List[torch.Tensor]:
        return [tensor * self.loss_weights[i] for i, tensor in enumerate(loss_tensors)]

    def _calc_loss(self, forward_batch: InferenceResultBatch) -> List[torch.Tensor]:
        return [loss_term(forward_batch) for loss_term in self.loss_terms]

    def __call__(self, eval_batch: InferenceResultBatch) -> torch.Tensor:
        loss_tensors = self._calc_loss(eval_batch)
        loss_tensors = self._scale(loss_tensors)
        loss_tensors = self._apply_loss_weights(loss_tensors)
        loss_tensor = torch.stack(loss_tensors).sum(dim=0)
        return loss_tensor
