#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import Dict, List
import pytest
from ml_gym.blueprints.constructables import TrainComponentConstructable, LossFunctionRegistryConstructable, \
    PredictionPostProcessingRegistryConstructable, Requirement,  DataLoadersConstructable, \
    MetricFunctionRegistryConstructable
from ml_gym.gym.post_processing import ArgmaxPostProcessorImpl
from ml_gym.gym.trainers.standard_trainer import TrainComponent
from ml_gym.loss_functions.loss_functions import CrossEntropyLoss
from pytests.blueprints.constructables.test_data_loader_constructable import CollatorFixture


class RegistryFixture:

    @pytest.fixture
    def prediction_postprocessing_registry(self):
        constructable = PredictionPostProcessingRegistryConstructable()
        postprocessing_fun_registry = constructable.construct()

        return postprocessing_fun_registry

    @pytest.fixture
    def loss_function_registry(self):
        constructable = LossFunctionRegistryConstructable()
        loss_fun_registry = constructable.construct()
        return loss_fun_registry

    @pytest.fixture
    def metric_registry(self):
        constructable = MetricFunctionRegistryConstructable()
        metric_fun_registry = constructable.construct()
        return metric_fun_registry


class DataLoaderFixture(CollatorFixture):
    @pytest.fixture
    def data_loader(self, informed_iterators, data_collator):
        sampling_strategies, drop_last, batch_size = {'train': {"strategy": "RANDOM", "seed": 0}}, True, 16
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"]),
                        "data_collator": Requirement(components=data_collator, subscription=["train", "test"])}
        constructable = DataLoadersConstructable(component_identifier="data_loader_component",
                                                 requirements=requirements,
                                                 batch_size=batch_size,
                                                 sampling_strategies=sampling_strategies,
                                                 drop_last=drop_last
                                                 )
        data_loader = constructable.construct()
        return data_loader


class TrainConfigFixture:
    @pytest.fixture
    def post_processors_config(self):
        post_processors_config: List[Dict] = [
            {"key": "ARG_MAX",
             "params": {"prediction_subscription_key": "model_prediction_key_anchor",
                        "prediction_publication_key": "postprocessing_argmax_key_anchor"}}]
        return post_processors_config

    @pytest.fixture
    def loss_fun_config(self):
        loss_fun_config: Dict = {"key": "CrossEntropyLoss", "target_subscription_key": "target_key",
                                 "prediction_subscription_key": "model_prediction_key"}

        return loss_fun_config

    @pytest.fixture
    def show_progress(self):
        return False


class TestTrainComponentConstructable(RegistryFixture, TrainConfigFixture):
    def test_constructable(self, prediction_postprocessing_registry, loss_function_registry, loss_fun_config,
                           post_processors_config, show_progress):
        requirements = {
            "prediction_postprocessing_registry": Requirement(components=prediction_postprocessing_registry),
            "loss_function_registry": Requirement(components=loss_function_registry)}

        constructable = TrainComponentConstructable(component_identifier="train_component_constructable",
                                                    requirements=requirements,
                                                    loss_fun_config=loss_fun_config,
                                                    post_processors_config=post_processors_config,
                                                    show_progress=show_progress
                                                    )
        train_component = constructable.construct()
        assert isinstance(train_component, TrainComponent)
        assert isinstance(train_component.post_processors[0].postprocessing_impl, ArgmaxPostProcessorImpl)
        assert isinstance(train_component.loss_fun, CrossEntropyLoss)
