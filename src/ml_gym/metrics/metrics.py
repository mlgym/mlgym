from typing import Callable, Dict, Any, Union, List
import torch
from sklearn.metrics import roc_auc_score, average_precision_score
from ml_gym.batching.batch import InferenceResultBatch
from abc import ABC, abstractmethod
import numpy as np
from torch import nn


def binary_auroc_score(y_true: torch.Tensor, y_pred: torch.Tensor, **params: Dict[str, Any]) -> float:
    score = roc_auc_score(y_true=y_true, y_score=y_pred, **params)
    return score


def binary_aupr_score(y_true: torch.Tensor, y_pred: torch.Tensor, **params: Dict[str, Any]) -> float:
    score = average_precision_score(y_true=y_true, y_score=y_pred, **params)
    return score


class MetricIF(ABC):

    @abstractmethod
    def __call__(self, result_batch: InferenceResultBatch) -> Any:
        raise NotImplementedError


class Metric(MetricIF):

    def __init__(self, tag: str, identifier: str):
        self.tag = tag
        self.identifier = identifier

    @abstractmethod
    def __call__(self, result_batch: InferenceResultBatch) -> float:
        raise NotImplementedError


class PredictionMetric(Metric):

    def __init__(self, tag: str, identifier: str, target_subscription_key: str,
                 prediction_subscription_key: str, metric_fun: Callable, params: Dict[str, Any]):
        super().__init__(tag=tag, identifier=identifier)
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.metric_fun = metric_fun
        self.params = params

    def __call__(self, result_batch: InferenceResultBatch) -> float:
        y_true = result_batch.get_targets(self.target_subscription_key).cpu()
        y_pred = result_batch.get_predictions(self.prediction_subscription_key).cpu()
        return self.metric_fun(y_true=y_true, y_pred=y_pred, **self.params)


class ClassSpecificExpectedCalibrationErrorMetric(Metric):

    def __init__(self, tag: str, identifier: str, target_subscription_key: str,
                 prediction_subscription_key: str, num_bins: int = 10, class_label: int = 1, sum_up_bins: bool = True):
        super().__init__(tag=tag, identifier=identifier)
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.num_bins = num_bins
        self.class_label = class_label
        self.bins = np.linspace(0, 1, self.num_bins+1)[1:-1]
        self.sum_up_bins = sum_up_bins

    def _calc_prevalence(self, y_true: torch.Tensor) -> torch.Tensor:
        # all positive samples / total population (within a single bin)
        return torch.sum(y_true == self.class_label)/float(len(y_true))

    def _calc_confidence(self, y_pred: torch.Tensor) -> torch.Tensor:
        # average confidence over all samples
        return torch.sum(y_pred) / len(y_pred)

    def _calc_calibration_error(self, y_true: torch.Tensor, y_pred: torch.Tensor) -> float:
        ece_score = torch.abs(self._calc_prevalence(y_true) - self._calc_confidence(y_pred))
        return float(ece_score)

    def __call__(self, result_batch: InferenceResultBatch) -> Union[float, List[float]]:
        y_true = result_batch.get_targets(self.target_subscription_key).cpu().flatten()
        y_pred = result_batch.get_predictions(self.prediction_subscription_key).cpu().flatten()  # confidence for single class

        # bin samples based on prediction confidence
        bin_indices = np.digitize(y_pred.detach().numpy(), bins=self.bins)
        ce_scores = []
        bin_weights = []
        for bin_indice in range(self.num_bins):
            bin_mask = bin_indices == bin_indice
            y_pred_bin = y_pred[bin_mask]
            y_true_bin = y_true[bin_mask]
            if len(y_pred_bin) > 0:
                ce_bin_score = self._calc_calibration_error(y_true=y_true_bin, y_pred=y_pred_bin)
                bin_weight = len(y_pred_bin)/len(y_pred)
                ce_scores.append(ce_bin_score)
                bin_weights.append(bin_weight)
            else:
                ce_scores.append(0)
                bin_weights.append(0)
        if self.sum_up_bins:
            ece_score = sum([score * weight for score, weight in zip(ce_scores, bin_weights)])
            return ece_score
        else:
            return ce_scores


class BinaryClasswiseExpectedCalibrationErrorMetric(Metric):

    def __init__(self, tag: str, identifier: str, target_subscription_key: str,
                 prediction_subscription_key_0: str, prediction_subscription_key_1: str, class_labels: List[int], num_bins: int = 10):
        super().__init__(tag=tag, identifier=identifier)
        self.class_labels = class_labels
        self.class_specific_ece_funs = [ClassSpecificExpectedCalibrationErrorMetric(tag="",
                                                                                    identifier="",
                                                                                    target_subscription_key=target_subscription_key,
                                                                                    prediction_subscription_key=prediction_subscription_key_0,
                                                                                    num_bins=num_bins,
                                                                                    class_label=0,
                                                                                    sum_up_bins=True),
                                        ClassSpecificExpectedCalibrationErrorMetric(tag="",
                                                                                    identifier="",
                                                                                    target_subscription_key=target_subscription_key,
                                                                                    prediction_subscription_key=prediction_subscription_key_1,
                                                                                    num_bins=num_bins,
                                                                                    class_label=1,
                                                                                    sum_up_bins=True), ]

    def __call__(self, result_batch: InferenceResultBatch) -> float:
        return np.mean([fun(result_batch) for fun in self.class_specific_ece_funs])


class BrierScoreMetric(Metric):
    def __init__(self, tag: str, identifier: str,
                 prediction_subscription_key: str,
                 target_subscription_key: str,
                 class_label: int = None):
        super().__init__(tag=tag, identifier=identifier)
        self.target_subscription_key = target_subscription_key
        self.prediction_subscription_key = prediction_subscription_key
        self.mse = nn.MSELoss(reduction="mean")
        self.class_label = class_label

    def __call__(self, inference_result_batch: InferenceResultBatch) -> float:
        y_true = inference_result_batch.get_targets(self.target_subscription_key).cpu().flatten()
        y_pred = inference_result_batch.get_predictions(self.prediction_subscription_key).cpu().flatten()
        if self.class_label is not None:
            mask = y_pred == self.class_label
            y_true = y_true[mask]
            y_pred = y_pred[mask]
        return self.mse(y_pred, y_true).item()
