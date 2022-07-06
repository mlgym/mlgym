import pytest
from ml_gym.metrics.metric_factory import MetricFactory
from ml_gym.metrics.metrics import PredictionMetric, BrierScoreMetric, RecallAtKMetric, AreaUnderRecallAtKMetric, \
    ClassSpecificExpectedCalibrationErrorMetric, BinaryClasswiseExpectedCalibrationErrorMetric


class TestMetricFactory:
    @pytest.fixture
    def target_subscription_key(self):
        target_key = "target_key"
        return target_key

    @pytest.fixture
    def prediction_key(self):
        prediction_key = "prediction_key"
        return prediction_key

    def test_get_brier_score_metric_fun(self, target_subscription_key, prediction_key):
        metric_func = MetricFactory.get_brier_score_metric_fun(target_subscription_key=target_subscription_key,
                                                               prediction_subscription_key=prediction_key,
                                                               tag=None)
        assert isinstance(metric_func, BrierScoreMetric)

    def test_get_recall_at_k_metric_fun(self, target_subscription_key, prediction_key):
        metric_func = MetricFactory.get_recall_at_k_metric_fun(target_subscription_key=target_subscription_key,
                                                               prediction_subscription_key=prediction_key,
                                                               tag=None,
                                                               class_label=1,
                                                               k_vals=[0, 1],
                                                               sort_descending=True)
        assert isinstance(metric_func, RecallAtKMetric)

    def test_get_area_under_recall_at_k_metric_fun(self, target_subscription_key, prediction_key):
        metric_func = MetricFactory.get_area_under_recall_at_k_metric_fun(
            target_subscription_key=target_subscription_key,
            prediction_subscription_key=prediction_key,
            tag=None,
            class_label=1,
            k_vals=[0, 1],
            sort_descending=True,
            normalize=True
        )
        assert isinstance(metric_func, AreaUnderRecallAtKMetric)

    def test_get_expected_calibration_error_metric_fun(self, target_subscription_key, prediction_key):
        metric_func = MetricFactory.get_expected_calibration_error_metric_fun(
            tag=None,
            target_subscription_key=target_subscription_key,
            prediction_subscription_key=prediction_key,
            num_bins=2,
            class_label=2,
            sum_up_bins=2
        )
        assert isinstance(metric_func, ClassSpecificExpectedCalibrationErrorMetric)

    def test_get_binary_classwise_expected_calibration_error_metric_fun(self, target_subscription_key, prediction_key):
        metric_func = MetricFactory.get_binary_classwise_expected_calibration_error_metric_fun(
            target_subscription_key=target_subscription_key,
            prediction_subscription_key_0=prediction_key,
            prediction_subscription_key_1=prediction_key,
            num_bins=2,
            class_labels=[2],
            tag=None)
        assert isinstance(metric_func, BinaryClasswiseExpectedCalibrationErrorMetric)
