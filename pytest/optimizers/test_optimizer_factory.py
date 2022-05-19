#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Dict, Any, Type
from copy import deepcopy

import pytest
from torch.optim import Optimizer, SGD, Adam, Adadelta
from ml_gym.optimizers.optimizer_factory import OptimizerFactory, OptimizerAdapter


class TestOptimizerFactory:
    @pytest.fixture
    def optimizer_factory(self) -> OptimizerFactory:
        return OptimizerFactory()

    @pytest.fixture
    def optimizer_params(self) -> Dict:
        return {"lr": 1.0, "momentum": 0.9}

    def test_get_optimizer(self, optimizer_factory: OptimizerFactory, optimizer_params: Dict):
        """
        To test OptimizerFactory.get_optimizer()
        """
        for key, optimizer_class in optimizer_factory.optimizer_map.items():
            optimizer: OptimizerAdapter = optimizer_factory.get_optimizer(key, optimizer_params)
            assert optimizer._optimizer_class == optimizer_class
            assert optimizer._optimizer_params == optimizer_params
