import pytest
import torch
from ml_gym.loss_functions.loss_scaler import MeanScaler, Scaler, NoScaler


class TestMeanScaler:
    @pytest.fixture
    def loss(self):
        return torch.Tensor([0, 1, 2, 3])

    @pytest.fixture
    def value(self):
        return 1

    def test_train(self, loss, value):
        mean_scaler = MeanScaler()
        mean_scaler.train(loss)
        assert mean_scaler.scale(value) == value / torch.mean(loss)

    def test_mean(self, value):
        mean_scaler = MeanScaler()
        mean_scaler.mean = 3
        assert mean_scaler.scale(value) == value / 3

    def test_state(self):
        state = {"mean": 2}
        mean_scaler = MeanScaler()
        mean_scaler.set_state(state)
        assert state["mean"] == mean_scaler.get_state()["mean"]


class TestNoScaler:
    @pytest.fixture
    def loss(self):
        return torch.Tensor([0, 1, 2, 3])

    @pytest.fixture
    def value(self):
        return 1

    def test_scale(self, loss, value):
        scaler = NoScaler()
        scaler.train(loss=loss)
        assert scaler.scale(value) == value
