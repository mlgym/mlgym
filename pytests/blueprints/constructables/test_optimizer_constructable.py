#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest
from ml_gym.blueprints.constructables import OptimizerConstructable
from ml_gym.optimizers.optimizer import OptimizerAdapter
from torch.optim import SGD, Adam, Adadelta


class TestOptimizerConstructable:
    @pytest.mark.parametrize('optimizer_key, params, class_name', [
        ("SGD", {"lr": 0, "momentum": 0.9}, SGD),
        ("SGD", {"lr": 0.5, "momentum": 0.9}, SGD),
        pytest.param("SGD", {"lr": 1.0}, Adam, marks=[pytest.mark.xfail]),
        ("ADAM", {"lr": 1.0}, Adam),
        ("ADADELTA", {"lr": 1.0}, Adadelta),
    ])
    def test_constructable(self, optimizer_key, params, class_name):
        constructable = OptimizerConstructable(optimizer_key=optimizer_key, params=params)
        optimizer_adapter = constructable.construct()

        assert isinstance(optimizer_adapter, OptimizerAdapter)
        assert optimizer_adapter._optimizer_class == class_name
        assert optimizer_adapter._optimizer_params == params
