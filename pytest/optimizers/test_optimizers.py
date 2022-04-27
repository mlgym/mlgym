from ml_gym.optimizers.optimizer import OptimizerAdapter
import pytest
import torch
from torch.nn import Module
from torch.nn.parameter import Parameter
from typing import List, Tuple
from torch.optim.sgd import SGD
from functools import partial
from copy import deepcopy


class TestOptimizerAdapter:
    num_samples = 10
    input_size = 5
    output_size = 1

    @pytest.fixture
    def model(self) -> Module:
        model = torch.nn.Sequential(
            torch.nn.Linear(TestOptimizerAdapter.input_size, 2),
            torch.nn.ReLU(),
            torch.nn.Linear(2, TestOptimizerAdapter.output_size))
        return model

    @pytest.fixture
    def optimizer(self) -> OptimizerAdapter:
        optimizer = OptimizerAdapter(SGD, {"lr": 1.0, "momentum": 0.9})
        return optimizer

    @pytest.fixture
    def data_batch(self) -> Tuple[torch.Tensor, torch.Tensor]:
        x = torch.randn(TestOptimizerAdapter.num_samples, TestOptimizerAdapter.input_size)
        y = torch.randn(TestOptimizerAdapter.num_samples, TestOptimizerAdapter.output_size)
        return x, y

    def test_register_model_params(self, optimizer: OptimizerAdapter, model):
        assert optimizer._optimizer is None
        optimizer.register_model_params(model_params=dict(model.named_parameters()))
        assert len(optimizer._optimizer.param_groups) > 0

    def test_optimizer_state_change(self, data_batch, model, optimizer: OptimizerAdapter):
        optimizer.register_model_params(model_params=dict(model.named_parameters()))
        optimizer_state_0 = deepcopy(optimizer.state_dict())

        x, y = data_batch
        loss_fn = torch.nn.MSELoss(reduction='sum')

        optimizer.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()

        optimizer_state_1 = deepcopy(optimizer.state_dict())

        optimizer.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()

        optimizer_state_2 = deepcopy(optimizer.state_dict())

        assert optimizer_state_0 != optimizer_state_1
        assert (optimizer_state_1["state"][0]["momentum_buffer"] != optimizer_state_2["state"][0]["momentum_buffer"]).all()

    def test_optimizer_state_recovery(self, data_batch, model, optimizer: OptimizerAdapter):
        optimizer.register_model_params(model_params=dict(model.named_parameters()))

        x, y = data_batch
        loss_fn = torch.nn.MSELoss(reduction='sum')

        optimizer.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()

        optimizer_state = deepcopy(optimizer.state_dict())
        optimizer.register_model_params(model_params=dict(model.named_parameters()))
        assert optimizer.state_dict() != optimizer_state
        optimizer.load_state_dict(optimizer_state)
        assert (optimizer.state_dict()["state"][0]["momentum_buffer"] == optimizer_state["state"][0]["momentum_buffer"]).all()