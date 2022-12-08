from copy import deepcopy
from typing import Dict, List, Tuple, Any

import pytest
from ml_gym.optimizers.optimizer import OptimizerAdapter
from torch.nn import Module
from torch.optim import SGD
from torch.optim.adam import Adam

from test_optimizers import TestOptimizerAdapter
from ml_gym.optimizers.optimizer import OptimizerBundle
import torch


class TestOptimizerBundle:
    @pytest.fixture
    def model(self) -> Module:
        model = torch.nn.Sequential(
            torch.nn.Linear(TestOptimizerAdapter.input_size, 2),
            torch.nn.ReLU(),
            torch.nn.Linear(2, TestOptimizerAdapter.output_size))
        return model

    @pytest.fixture
    def optimizer_adapters(self) -> Dict[str, OptimizerAdapter]:
        optimizer_adapters = {"SGD": OptimizerAdapter(SGD, {"lr": 1.0, "momentum": 0.9}),
                              "ADAM": OptimizerAdapter(Adam, {"lr": 1.0})}
        return optimizer_adapters

    @pytest.fixture
    def optimizer_key_to_param_key_filters(self, model) -> Dict[str, List[str]]:
        optimizer_key_to_param_key_filters = {"SGD": list(dict(model.named_parameters()).keys()),
                                              "ADAM": list(dict(model.named_parameters()).keys())}
        return optimizer_key_to_param_key_filters

    @pytest.fixture
    def data_batch(self) -> Tuple[torch.Tensor, torch.Tensor]:
        x = torch.randn(TestOptimizerAdapter.num_samples, TestOptimizerAdapter.input_size)
        y = torch.randn(TestOptimizerAdapter.num_samples, TestOptimizerAdapter.output_size)
        return x, y

    @pytest.fixture
    def optimizer_bundle(self, optimizer_adapters, optimizer_key_to_param_key_filters) -> OptimizerBundle:
        optimizer_bundle = OptimizerBundle(optimizer_adapters, optimizer_key_to_param_key_filters)
        return optimizer_bundle

    @pytest.fixture
    def optimizer_state_dict(self, optimizer_bundle, model, data_batch) -> Dict[str, Any]:
        # To have a state dict
        optimizer_bundle = deepcopy(optimizer_bundle)
        optimizer_bundle.register_model_params(model_params=dict(model.named_parameters()), restore_state=True)
        x, y = data_batch
        loss_fn = torch.nn.MSELoss(reduction='sum')

        optimizer_bundle.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer_bundle.step()

        optimizer_state_1 = deepcopy(optimizer_bundle.state_dict())

        return optimizer_state_1

    def test_register_model_params(self, optimizer_bundle: OptimizerBundle, model):
        for optimizer_key in optimizer_bundle.optimizers.keys():
            assert optimizer_bundle.optimizers[optimizer_key]._optimizer is None

        optimizer_bundle.register_model_params(model_params=dict(model.named_parameters()), restore_state=True)
        for optimizer_key in optimizer_bundle.optimizers.keys():
            assert len(optimizer_bundle.optimizers[optimizer_key]._optimizer.param_groups) > 0

    def test_optimizers_state_change(self, data_batch, model, optimizer_bundle: OptimizerBundle, optimizer_adapters):
        optimizer_bundle.register_model_params(model_params=dict(model.named_parameters()), restore_state=True)
        optimizer_state_0 = deepcopy(optimizer_bundle.state_dict())

        x, y = data_batch
        loss_fn = torch.nn.MSELoss(reduction='sum')

        optimizer_bundle.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer_bundle.step()

        optimizer_state_1 = deepcopy(optimizer_bundle.state_dict())

        optimizer_bundle.zero_grad()
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer_bundle.step()
        optimizer_state_2 = deepcopy(optimizer_bundle.state_dict())

        optimizer_bundle.zero_grad(optimizer_id="SGD")
        output = model(x)
        loss = loss_fn(output, y)
        loss.backward()
        optimizer_bundle.step(optimizer_id="SGD")
        optimizer_state_3 = deepcopy(optimizer_bundle.state_dict())

        assert optimizer_state_0 != optimizer_state_1
        assert (optimizer_state_2["ADAM"]["state"][0]["exp_avg"] == optimizer_state_3["ADAM"]["state"][0]["exp_avg"]).all()
        assert (optimizer_state_2["SGD"]["state"][0]["momentum_buffer"] != optimizer_state_3["SGD"]["state"][0][
            "momentum_buffer"]).all()

        assert (optimizer_state_1["SGD"]["state"][0]["momentum_buffer"] != optimizer_state_2["SGD"]["state"][0][
            "momentum_buffer"]).all()

    def test_load_state_dict(self, optimizer_bundle: OptimizerBundle, model, optimizer_state_dict):
        # test when the optimizer._optimizer is None and self._state_dict is not None
        # Firstly load state dict for optimizer, to make optimizer._state_dict not None
        for optimizer_key in optimizer_bundle.optimizers.keys():
            assert optimizer_bundle.optimizers[optimizer_key]._optimizer is None

        optimizer_bundle.load_state_dict(state_dict=optimizer_state_dict)
        for optimizer_key in optimizer_bundle.optimizers.keys():
            assert optimizer_bundle.optimizers[optimizer_key].state_dict() == optimizer_state_dict[optimizer_key]
