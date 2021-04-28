import pytest
import torch
from ml_gym.batching.batch import InferenceResultBatch
from ml_gym.metrics.metrics import binary_aupr_score, binary_auroc_score, PredictionMetric, ClassSpecificExpectedCalibrationErrorMetric, \
    BrierScoreMetric, BinaryClasswiseExpectedCalibrationErrorMetric
from ml_gym.metrics.metric_factory import MetricFactory
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


class TestClasswiseExpectedCalibrationError:
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

    def test_calc_metric(self, probability_inference_batch_result: InferenceResultBatch):
        ece_metric = BinaryClasswiseExpectedCalibrationErrorMetric(tag="tag",
                                                                   identifier="identifier",
                                                                   target_subscription_key=self.target_key,
                                                                   prediction_subscription_key_1=self.prediction_probability_key,
                                                                   num_bins=10,
                                                                   class_labels=[0, 1])

        ece_metric_0 = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                   identifier="identifier",
                                                                   target_subscription_key=self.target_key,
                                                                   prediction_subscription_key=self.prediction_probability_key,
                                                                   num_bins=10,
                                                                   class_label=0)

        ece_metric_1 = ClassSpecificExpectedCalibrationErrorMetric(tag="tag",
                                                                   identifier="identifier",
                                                                   target_subscription_key=self.target_key,
                                                                   prediction_subscription_key=self.prediction_probability_key,
                                                                   num_bins=10,
                                                                   class_label=1)

        ece_score_0 = ece_metric_0(probability_inference_batch_result)
        ece_score_1 = ece_metric_1(probability_inference_batch_result)

        ece_score = ece_metric(probability_inference_batch_result)
        assert ece_score == (ece_score_0 + ece_score_1) / 2


class TestBrierScoreMetric:

    @pytest.fixture
    def brier_fun(self):
        return MetricFactory.get_brier_score_metric_fun(tag="sample_tag",
                                                        prediction_subscription_key="predictions",
                                                        target_subscription_key="targets")

    @pytest.mark.parametrize(
        "targets", [[0, 1, 0, 1], [0, 0, 0, 1]])
    @pytest.mark.parametrize(
        "predictions", [[0.5, 0, 0, 0.5], [0.5, 0.24, 0.56, 0.56]]
    )
    def test_brier_score(self, targets, predictions, brier_fun):
        target_tensor = torch.tensor(targets)
        prediction_tensor = torch.tensor(predictions)
        targets = {"targets": target_tensor}
        predictions = {"predictions": prediction_tensor}
        inference_result_batch = InferenceResultBatch(targets=targets, predictions=predictions,
                                                      tags="simple_tag")

        result = brier_fun(inference_result_batch=inference_result_batch)
        reference_result = torch.sum((target_tensor-prediction_tensor)**2) / len(target_tensor)
        assert reference_result == result


class TestRecallAtKMetric:

    @pytest.fixture
    def recall_at_k_metric_fun(self):
        return MetricFactory.get_recall_at_k_metric_fun(tag="sample_tag",
                                                        prediction_subscription_key=TestMetrics.prediction_key,
                                                        target_subscription_key=TestMetrics.target_key,
                                                        class_label=1,
                                                        k_vals=[2, 3],
                                                        sort_descending=True)

    @pytest.fixture
    def inference_result_batch(self) -> InferenceResultBatch:
        targets = torch.IntTensor([1, 1, 0, 0, 0, 1, 1])
        predictions = torch.FloatTensor([0, 0.2, 0.1, 0.01, 0.9, 0.7, 1])
        return InferenceResultBatch(targets={TestMetrics.target_key: targets},
                                    predictions={TestMetrics.prediction_key: predictions},
                                    tags=None)

    def test_metric_fun(self, recall_at_k_metric_fun, inference_result_batch: InferenceResultBatch):
        result = recall_at_k_metric_fun(inference_result_batch=inference_result_batch)
        assert [1/4, 2/4] == result
