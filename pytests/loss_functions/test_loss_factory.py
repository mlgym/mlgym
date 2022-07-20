import pytest
from ml_gym.loss_functions.loss_factory import LossFactory
from ml_gym.loss_functions.loss_functions import LPLoss, CrossEntropyLoss, NLLLoss, BCEWithLogitsLoss, BCELoss


class TestLossFactory:
    @pytest.fixture
    def target_subscription_key(self):
        target_key = "target_key"
        return target_key

    @pytest.fixture
    def prediction_key(self):
        prediction_key = "prediction_key"
        return prediction_key

    def test_get_lp_loss(self, target_subscription_key, prediction_key):
        loss_func = LossFactory.get_lp_loss(target_subscription_key, prediction_key)
        assert isinstance(loss_func, LPLoss)

    def test_get_cross_entropy_loss(self, target_subscription_key, prediction_key):
        loss_func = LossFactory.get_cross_entropy_loss(target_subscription_key, prediction_key)
        assert isinstance(loss_func, CrossEntropyLoss)

    def test_get_nll_loss(self, target_subscription_key, prediction_key):
        loss_func = LossFactory.get_nll_loss(target_subscription_key, prediction_key)
        assert isinstance(loss_func, NLLLoss)

    def test_get_bce_with_logits_loss(self, target_subscription_key, prediction_key):
        loss_func = LossFactory.get_bce_with_logits_loss(target_subscription_key, prediction_key)
        assert isinstance(loss_func, BCEWithLogitsLoss)

    def test_get_bce_loss(self, target_subscription_key, prediction_key):
        loss_func = LossFactory.get_bce_loss(target_subscription_key, prediction_key)
        assert isinstance(loss_func, BCELoss)
