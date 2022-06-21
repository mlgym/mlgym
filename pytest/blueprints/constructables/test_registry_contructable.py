#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest
from ml_gym.blueprints.constructables import ModelRegistryConstructable, LossFunctionRegistryConstructable, \
    MetricFunctionRegistryConstructable, PredictionPostProcessingRegistryConstructable, Requirement, ModelConstructable
from typing import Dict
import torch
from ml_gym.models.nn.net import NNModel
from ml_gym.registries.class_registry import ClassRegistry

from mocked_classes import MockedNNModel


class ModelFixtures:

    @pytest.fixture
    def mocked_nn_class(self):
        return MockedNNModel

    @pytest.fixture
    def seed(self):
        return 0

    @pytest.fixture
    def layer_config(self):
        return {}

    @pytest.fixture
    def prediction_publication_key(self):
        return ""

    @pytest.fixture
    def model_registry(self, mocked_nn_class):
        constructable = ModelRegistryConstructable()
        model_registry = constructable.construct()
        model_registry.add_class("mocked_nn", mocked_nn_class)
        return model_registry


class TestModelRegistryConstructable(ModelFixtures):
    def test_constructable(self, mocked_nn_class, seed, layer_config, prediction_publication_key):
        constructable = ModelRegistryConstructable()
        model_registry = constructable.construct()
        model_registry.add_class("mocked_nn", mocked_nn_class)

        assert isinstance(model_registry, ClassRegistry)
        assert model_registry._store["mocked_nn"] == mocked_nn_class

        # assert if it is able to get a model instance using model_registry
        model = model_registry.get_instance("mocked_nn", seed=seed, layer_config=layer_config,
                                            prediction_publication_key=prediction_publication_key)
        assert isinstance(model, mocked_nn_class)


class TestModelConstructable(ModelFixtures):
    def test_constructable(self, mocked_nn_class):
        # use model registry to register a model class
        requirements = {"model_registry": Requirement(components=mocked_nn_class)}
        model_definition = {}
        seed = 0
        prediction_publication_keys = {}
        constructable = ModelConstructable(component_identifier="model_component",
                                           requirements=requirements,
                                           model_type="mocked_nn",
                                           model_definition=model_definition,
                                           seed=seed,
                                           prediction_publication_keys=prediction_publication_keys)
        model = constructable.construct()
        assert isinstance(model, mocked_nn_class)


class TestLossFunctionRegistryConstructable:
    def test_constructable(self):
        constructable = LossFunctionRegistryConstructable()
        loss_fun_registry = constructable.construct()
        assert isinstance(loss_fun_registry, ClassRegistry)
        assert len(loss_fun_registry._store) != 0


class TestMetricFunctionRegistryConstructable:
    def test_constructable(self):
        constructable = MetricFunctionRegistryConstructable()
        metric_fun_registry = constructable.construct()
        assert len(metric_fun_registry._store) != 0
        assert isinstance(metric_fun_registry, ClassRegistry)


class TestPredictionPostProcessingRegistryConstructable:
    def test_constructable(self):
        constructable = PredictionPostProcessingRegistryConstructable()
        postprocessing_fun_registry = constructable.construct()
        assert len(postprocessing_fun_registry._store) != 0
        assert isinstance(postprocessing_fun_registry, ClassRegistry)
