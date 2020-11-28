import pytest
import torch
from ml_gym.batch import InferenceResultBatch
from ml_gym.metrics.metrics import binary_aupr_score, binary_auroc_score, Metric


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
        metric_fun = Metric(target_subscription_key=TestMetrics.target_key,
                            prediction_subscription_key=TestMetrics.prediction_key,
                            tag="aupr",
                            identifier="aupr",
                            metric_fun=binary_aupr_score,
                            params={"average": "macro"})
        aupr_good = metric_fun(probability_inference_batch_result_good)
        aupr_bad = metric_fun(probability_inference_batch_result_bad)
        assert aupr_good > aupr_bad

    def test_binary_auroc_score(self, probability_inference_batch_result_good, probability_inference_batch_result_bad):
        metric_fun = Metric(target_subscription_key=TestMetrics.target_key,
                            prediction_subscription_key=TestMetrics.prediction_key,
                            tag="auroc",
                            identifier="auroc",
                            metric_fun=binary_auroc_score,
                            params={"average": "macro"})
        auroc_good = metric_fun(probability_inference_batch_result_good)
        auroc_bad = metric_fun(probability_inference_batch_result_bad)
        assert auroc_good > auroc_bad
