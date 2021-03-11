from typing import Callable, Dict, Any, List
from functools import partial
from ml_gym.metrics.metrics import BinaryClasswiseExpectedCalibrationErrorMetric, PredictionMetric, BrierScoreMetric, \
    ClassSpecificExpectedCalibrationErrorMetric

from ml_gym.batching.batch import InferenceResultBatch


class MetricFactory:

    @staticmethod
    def get_sklearn_metric(metric_key: str, metric_fun: Callable,  params: Dict = None) -> Callable[[InferenceResultBatch], Any]:
        if params is None:
            params = {}
        return partial(PredictionMetric, identifier=metric_key, metric_fun=metric_fun, **params)

    @staticmethod
    def get_brier_score_metric_fun(tag: str,
                                   prediction_subscription_key: str,
                                   target_subscription_key: str):
        brier_score_fun = BrierScoreMetric(tag=tag,
                                           identifier="BRIER_SCORE",
                                           prediction_subscription_key=prediction_subscription_key,
                                           target_subscription_key=target_subscription_key)
        return brier_score_fun

    @staticmethod
    def get_expected_calibration_error_metric_fun(tag: str,
                                                  prediction_subscription_key: str,
                                                  target_subscription_key: str,
                                                  num_bins: int,
                                                  class_label: int,
                                                  sum_up_bins: bool):
        ece_score_fun = ClassSpecificExpectedCalibrationErrorMetric(tag=tag,
                                                                    identifier="EXPECTED_CALIBRATION_ERROR",
                                                                    prediction_subscription_key=prediction_subscription_key,
                                                                    target_subscription_key=target_subscription_key,
                                                                    num_bins=num_bins,
                                                                    class_label=class_label,
                                                                    sum_up_bins=sum_up_bins)
        return ece_score_fun

    @staticmethod
    def get_binary_classwise_expected_calibration_error_metric_fun(tag: str,
                                                                   target_subscription_key: str,
                                                                   prediction_subscription_key_0: str,
                                                                   prediction_subscription_key_1: str,
                                                                   num_bins: int,
                                                                   class_labels: List[int]):
        ece_score_fun = BinaryClasswiseExpectedCalibrationErrorMetric(tag=tag,
                                                                      identifier="BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR",
                                                                      prediction_subscription_key_0=prediction_subscription_key_0,
                                                                      prediction_subscription_key_1=prediction_subscription_key_1,
                                                                      target_subscription_key=target_subscription_key,
                                                                      num_bins=num_bins,
                                                                      class_labels=class_labels)
        return ece_score_fun
