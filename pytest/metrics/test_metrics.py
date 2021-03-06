import pytest
import torch
from ml_gym.batching.batch import InferenceResultBatch
from ml_gym.metrics.metrics import binary_aupr_score, binary_auroc_score, PredictionMetric, ClassSpecificExpectedCalibrationErrorMetric
import numpy as np


class TestMetrics:
    target_key = "target_key"
    prediction_key = "prediction_key"

    @pytest.fixture
    def probability_inference_batch_result_good(self) -> InferenceResultBatch:
        targets = torch.IntTensor([0, 0, 0, 1, 1, 1])  # [batch_size]
        predictions = torch.FloatTensor([0, 0.1, 0.01, 0.9, 0.7, 1])
        return InferenceResultBatch(targets={TestMetrics.target_key: targets},
                                    predictions={TestMetrics.prediction_key: predictions},
                                    tags=None)

    @pytest.fixture
    def probability_inference_batch_result_bad(self) -> InferenceResultBatch:
        targets = torch.IntTensor([0, 0, 0, 1, 1, 1])  # [batch_size]
        predictions = torch.FloatTensor([1, 0.9, 0.01, 0.1, 0.2, 0.1])
        return InferenceResultBatch(targets={TestMetrics.target_key: targets},
                                    predictions={TestMetrics.prediction_key: predictions},
                                    tags=None)

    def test_binary_aupr_score(self, probability_inference_batch_result_good, probability_inference_batch_result_bad):
        metric_fun = PredictionMetric(target_subscription_key=TestMetrics.target_key,
                                      prediction_subscription_key=TestMetrics.prediction_key,
                                      tag="aupr",
                                      identifier="aupr",
                                      metric_fun=binary_aupr_score,
                                      params={"average": "macro"})
        aupr_good = metric_fun(probability_inference_batch_result_good)
        aupr_bad = metric_fun(probability_inference_batch_result_bad)
        assert aupr_good > aupr_bad

    def test_binary_auroc_score(self, probability_inference_batch_result_good, probability_inference_batch_result_bad):
        metric_fun = PredictionMetric(target_subscription_key=TestMetrics.target_key,
                                      prediction_subscription_key=TestMetrics.prediction_key,
                                      tag="auroc",
                                      identifier="auroc",
                                      metric_fun=binary_auroc_score,
                                      params={"average": "macro"})
        auroc_good = metric_fun(probability_inference_batch_result_good)
        auroc_bad = metric_fun(probability_inference_batch_result_bad)
        assert auroc_good > auroc_bad


class TestExpectedCalibrationError:
    target_key = "target_key"
    prediction_probability_key = "prediction_probability_key"
    prediction_class_key = "prediction_class_key"

    @pytest.fixture
    def probability_inference_batch_result(self) -> InferenceResultBatch:
        targets = torch.IntTensor([0, 0, 0, 1, 0, 1, 1])  # [batch_size]
        prediction_probabilities = torch.FloatTensor([0, 0.01, 0.05, 0.91, 0.92, 1, 0.96])
        return InferenceResultBatch(targets={TestExpectedCalibrationError.target_key: targets},
                                    predictions={TestExpectedCalibrationError.prediction_probability_key: prediction_probabilities},
                                    tags=None)

    def test__calc_prevalence(self, probability_inference_batch_result: InferenceResultBatch):
        ece_metric = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                 identifier="identifier",
                                                                 target_subscription_key=self.target_key,
                                                                 prediction_subscription_key=self.prediction_probability_key,
                                                                 num_bins=10,
                                                                 class_label=1)
        y_true = probability_inference_batch_result.targets[self.target_key]
        prevalence = ece_metric._calc_prevalence(y_true)
        assert prevalence == 3/7

    def test__calc_confidence(self, probability_inference_batch_result: InferenceResultBatch):
        ece_metric = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                 identifier="identifier",
                                                                 target_subscription_key=self.target_key,
                                                                 prediction_subscription_key=self.prediction_probability_key,
                                                                 num_bins=10,
                                                                 class_label=1)
        y_pred = probability_inference_batch_result.predictions[self.prediction_probability_key]
        conf = ece_metric._calc_confidence(y_pred)
        assert conf == torch.mean(y_pred)

    def test__calc_calibration_error(self, probability_inference_batch_result: InferenceResultBatch):
        ece_metric = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                 identifier="identifier",
                                                                 target_subscription_key=self.target_key,
                                                                 prediction_subscription_key=self.prediction_probability_key,
                                                                 num_bins=10,
                                                                 class_label=1)
        y_true = probability_inference_batch_result.targets[self.target_key]
        y_pred_proba = probability_inference_batch_result.predictions[self.prediction_probability_key]

        ece_score = ece_metric._calc_calibration_error(y_true, y_pred_proba)
        assert ece_score == abs(torch.mean(y_pred_proba) - 3/7)

    def test__calc_expcted_ce_summed(self, probability_inference_batch_result: InferenceResultBatch):
        ece_metric = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                 identifier="identifier",
                                                                 target_subscription_key=self.target_key,
                                                                 prediction_subscription_key=self.prediction_probability_key,
                                                                 num_bins=10,
                                                                 class_label=1)
        ece_score_reference = 3/7 * np.abs(0/3-np.mean([0, 0.01, 0.05])) + 4/7*np.abs(3/4 - np.mean([0.91, 0.92, 1, 0.96]))
        ece_score = ece_metric(probability_inference_batch_result)
        assert abs(ece_score-ece_score_reference) < 0.00001

    def test__calc_expcted_ce_not_summed(self, probability_inference_batch_result: InferenceResultBatch):
        ece_metric = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                 identifier="identifier",
                                                                 target_subscription_key=self.target_key,
                                                                 prediction_subscription_key=self.prediction_probability_key,
                                                                 num_bins=10,
                                                                 class_label=1,
                                                                 sum_up_bins=False)
        ce_scores_reference = [np.abs(0/3-np.mean([0, 0.01, 0.05])), 0, 0, 0, 0, 0, 0, 0, 0, np.abs(3/4 - np.mean([0.91, 0.92, 1, 0.96]))]
        ce_scores = ece_metric(probability_inference_batch_result)
        assert np.sum(np.abs(np.array(ce_scores_reference) - np.array(ce_scores))) < 0.00001
