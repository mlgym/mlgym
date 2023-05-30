from typing import Callable, Dict, Any, List
from functools import partial
from ml_gym.metrics.metrics import BinaryClasswiseExpectedCalibrationErrorMetric, PredictionMetric, BrierScoreMetric, \
    ClassSpecificExpectedCalibrationErrorMetric, RecallAtKMetric, AreaUnderRecallAtKMetric

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
        """
        Get BRIER Score Metric
        :params:
            - tag (str): Label to be tagged with the metric object.
            - prediction_subscription_key (str): Subscription key to the prediction table.
            - target_subscription_key (str): Subscription key to the target table.

        :returns:
            brier_score_fun (BrierScoreMetric): BrierScoreMetric object.
        """
        brier_score_fun = BrierScoreMetric(tag=tag,
                                           identifier="BRIER_SCORE",
                                           prediction_subscription_key=prediction_subscription_key,
                                           target_subscription_key=target_subscription_key)
        return brier_score_fun

    @staticmethod
    def get_recall_at_k_metric_fun(tag: str,
                                   prediction_subscription_key: str,
                                   target_subscription_key: str,
                                   class_label: int,
                                   k_vals: List[int],
                                   sort_descending: bool):
        """
        Get Recall at K Metric
        :params:
            - tag (str): Label to be tagged with the metric object.
            - prediction_subscription_key (str): Subscription key to the prediction table.
            - target_subscription_key (str): Subscription key to the target table.
            - class_label (int): Class label.
            - k_vals (List[int]): List of k values.
            - sort_descending (bool): Sort descending.

        :returns:
            recall_at_k_metric_fun (RecallAtKMetric): RecallAtKMetric object.
        """
        recall_at_k_metric_fun = RecallAtKMetric(tag=tag,
                                                 identifier="RecallAtK",
                                                 prediction_subscription_key=prediction_subscription_key,
                                                 target_subscription_key=target_subscription_key,
                                                 class_label=class_label,
                                                 k_vals=k_vals,
                                                 sort_descending=sort_descending)
        return recall_at_k_metric_fun

    @staticmethod
    def get_area_under_recall_at_k_metric_fun(tag: str,
                                              prediction_subscription_key: str,
                                              target_subscription_key: str,
                                              class_label: int,
                                              k_vals: List[int],
                                              sort_descending: bool,
                                              normalize: bool):
        """
        Get Area Under Recall at K Metric
        :params:
            - tag (str): Label to be tagged with the metric object.
            - prediction_subscription_key (str): Subscription key to the prediction table.
            - target_subscription_key (str): Subscription key to the target table.
            - class_label (int): Class label.
            - k_vals (List[int]): List of k values.
            - sort_descending (bool): Sort descending.
            - normalize (bool): Normalize.

        :returns:
            area_under_recall_at_k_metric_fun (AreaUnderRecallAtKMetric): AreaUnderRecallAtKMetric object.
        """
        area_under_recall_at_k_metric_fun = AreaUnderRecallAtKMetric(tag=tag,
                                                                     identifier="RecallAtK",
                                                                     prediction_subscription_key=prediction_subscription_key,
                                                                     target_subscription_key=target_subscription_key,
                                                                     class_label=class_label,
                                                                     k_vals=k_vals,
                                                                     sort_descending=sort_descending,
                                                                     normalize=normalize)
        return area_under_recall_at_k_metric_fun

    @staticmethod
    def get_expected_calibration_error_metric_fun(tag: str,
                                                  prediction_subscription_key: str,
                                                  target_subscription_key: str,
                                                  num_bins: int,
                                                  class_label: int,
                                                  sum_up_bins: bool):
        """
        Get Expected Calibration Error Metric
        :params:
            - tag (str): Label to be tagged with the metric object.
            - prediction_subscription_key (str): Subscription key to the prediction table.
            - target_subscription_key (str): Subscription key to the target table.
            - num_bins (int): Number of bins.
            - class_label (int): Class label.
            - sum_up_bins (bool): Sum up bins.

        :returns:
            ece_score_fun (ClassSpecificExpectedCalibrationErrorMetric): ClassSpecificExpectedCalibrationErrorMetric object.
        """
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
        """
        Get Binary Classwise Expected Calibration Error Metric
        :params:
            - tag (str): Label to be tagged with the metric object.
            - target_subscription_key (str): Subscription key to the target table.
            - prediction_subscription_key_0 (str): Subscription key to the prediction table for class 0.
            - prediction_subscription_key_1 (str): Subscription key to the prediction table for class 1.
            - num_bins (int): Number of bins.
            - class_label (int): Class label.

        :returns:
            ece_score_fun (BinaryClasswiseExpectedCalibrationErrorMetric): BinaryClasswiseExpectedCalibrationErrorMetric object.
        """
        ece_score_fun = BinaryClasswiseExpectedCalibrationErrorMetric(tag=tag,
                                                                      identifier="BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR",
                                                                      prediction_subscription_key_0=prediction_subscription_key_0,
                                                                      prediction_subscription_key_1=prediction_subscription_key_1,
                                                                      target_subscription_key=target_subscription_key,
                                                                      num_bins=num_bins,
                                                                      class_labels=class_labels)
        return ece_score_fun
