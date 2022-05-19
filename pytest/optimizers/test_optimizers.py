from ml_gym.optimizers.optimizer import OptimizerAdapter
import pytest
import torch
from torch.nn import Module
from torch.nn.parameter import Parameter
from typing import List, Tuple, Dict, Any
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
    def false_restore_state(self) -> bool:
        return False

    @pytest.fixture
    def optimizer_state_dict(self, model, data_batch) -> Dict[str, Any]:
        # To have a state dict
        optimizer = OptimizerAdapter(SGD, {"lr": 1.0, "momentum": 0.9})
        optimizer.register_model_params(model_params=dict(model.named_parameters()))
        x, y = data_batch
        loss_fn = torch.nn.MSELoss(reduction='sum')

        optimizer.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer.step()

        optimizer_state_1 = deepcopy(optimizer.state_dict())

        return optimizer_state_1

    @pytest.fixture
    def data_batch(self) -> Tuple[torch.Tensor, torch.Tensor]:
        x = torch.randn(TestOptimizerAdapter.num_samples, TestOptimizerAdapter.input_size)
        y = torch.randn(TestOptimizerAdapter.num_samples, TestOptimizerAdapter.output_size)
        return x, y

    def test_register_model_params(self, optimizer: OptimizerAdapter, model):
        assert optimizer._optimizer is None
        optimizer.register_model_params(model_params=dict(model.named_parameters()))
        assert len(optimizer._optimizer.param_groups) > 0

    def test_register_model_params_without_restore_state(self, optimizer: OptimizerAdapter, model, false_restore_state):
        # If not restore_state,
        # reinitialize the optimizer._optimizer with given model_params,
        # no matter the optimizer._optimizer is None or not
        optimizer.register_model_params(model_params=dict(model.named_parameters()), restore_state=false_restore_state)
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
        assert (optimizer_state_1["state"][0]["momentum_buffer"] != optimizer_state_2["state"][0][
            "momentum_buffer"]).all()

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

        # assert optimizer.state_dict() != optimizer_state
        # set restore_state, register_model_params() function can load_state_dict() in the itself.
        # To cover line #23 in optimizer.py
        optimizer.register_model_params(model_params=dict(model.named_parameters()), restore_state=True)
        assert (optimizer.state_dict()["state"][0]["momentum_buffer"] == optimizer_state["state"][0][
            "momentum_buffer"]).all()

    def test_load_state_dict(self, optimizer: OptimizerAdapter, model, optimizer_state_dict):
        # test when the optimizer._optimizer is None and self._state_dict is not None
        # Firstly load state dict for optimizer, to make optimizer._state_dict not None
        assert optimizer._optimizer is None
        optimizer.load_state_dict(state_dict=optimizer_state_dict)
        assert optimizer.state_dict() == optimizer_state_dict

        # initialize a optimizer._optimizer,
        # it would load the state dict from optimizer._state_dict for optimizer._optimizer
        assert optimizer._optimizer is None and optimizer._state_dict is not None
        optimizer.register_model_params(model_params=dict(model.named_parameters()))

        # check if optimizer._optimizer.state_dict() same with the optimizer_state_dict
        assert (optimizer._optimizer.state_dict()["state"][0]["momentum_buffer"] == optimizer.state_dict()["state"][0][
            "momentum_buffer"]).all()
        assert (optimizer.state_dict()["state"][0]["momentum_buffer"] == optimizer_state_dict["state"][0][
            "momentum_buffer"]).all()
        assert optimizer._state_dict is None

    def test_deep_copy(self, optimizer: OptimizerAdapter, model):
        # Test for OptimizerAdapter.__deepcopy__() function
        optimizer.register_model_params(model_params=dict(model.named_parameters()))
        optimizer_copy = deepcopy(optimizer)
        for (k, v), (k_copy, v_copy) in zip(optimizer.__dict__.items(), optimizer_copy.__dict__.items()):
            assert k == k_copy
