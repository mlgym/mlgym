#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import List, Dict

import pytest
from ml_gym.blueprints.constructables import Requirement, EvalComponentConstructable
from ml_gym.gym.evaluator import EvalComponent
from test_train_component_constructable import RegistryFixture, DataLoaderFixture


class EvalConfigFixture:
    @pytest.fixture
    def metrics_config(self):
        metrics_config: List = [{"key": "F1_SCORE",
                                 "params": {"average": "macro"},
                                 "prediction_subscription_key": "model_prediction_key",
                                 "target_subscription_key": "target_key",
                                 "tag": "F1_SCORE_macro"}]
        return metrics_config

    @pytest.fixture
    def train_split_name(self):
        train_split_name: str = "train"
        return train_split_name

    @pytest.fixture
    def loss_funs_config(self):
        loss_funs_config: List = [
            {"prediction_subscription_key": "model_prediction_key",
             "target_subscription_key": "target_key",
             "key": "CrossEntropyLoss",
             "tag": "cross_entropy_loss"}]
        return loss_funs_config

    @pytest.fixture
    def post_processors_config(self):
        post_processors_config: List = [{
            "key": "ARG_MAX",
            "prediction_subscription_key": "model_prediction_key",
            "prediction_publication_key": "postprocessing_argmax_key"
        }]
        return post_processors_config

    @pytest.fixture
    def show_progress(self) -> bool:
        return False

    @pytest.fixture
    def cpu_target_subscription_keys(self) -> List[str]:
        cpu_target_subscription_keys: List[str] = ["target_key"]
        return cpu_target_subscription_keys

    @pytest.fixture
    def cpu_prediction_subscription_keys(self) -> List[str]:
        cpu_prediction_subscription_keys: List[str] = ["postprocessing_argmax_key", "model_prediction_key"]
        return cpu_prediction_subscription_keys

    @pytest.fixture
    def metrics_computation_config(self) -> List[Dict]:
        metrics_computation_config: List[Dict] = None
        return metrics_computation_config

    @pytest.fixture
    def loss_computation_config(self) -> List[Dict]:
        loss_computation_config: List[Dict] = None
        return loss_computation_config


class TestEvalComponentConstructable(RegistryFixture, DataLoaderFixture, EvalConfigFixture):
    def test_constructable(self, data_loader, prediction_postprocessing_registry, loss_function_registry,
                           metric_registry, train_split_name, metrics_config, loss_funs_config, post_processors_config,
                           cpu_target_subscription_keys, cpu_prediction_subscription_keys, metrics_computation_config,
                           loss_computation_config, show_progress
                           ):
        requirements = {
            "data_loaders": Requirement(components=data_loader),
            "prediction_postprocessing_registry": Requirement(components=prediction_postprocessing_registry),
            "loss_function_registry": Requirement(components=loss_function_registry),
            "metric_registry": Requirement(components=metric_registry),
        }

        constructable = EvalComponentConstructable(component_identifier="eval_component_constructable",
                                                   requirements=requirements,
                                                   train_split_name=train_split_name,
                                                   metrics_config=metrics_config,
                                                   loss_funs_config=loss_funs_config,
                                                   post_processors_config=post_processors_config,
                                                   cpu_target_subscription_keys=cpu_target_subscription_keys,
                                                   cpu_prediction_subscription_keys=cpu_prediction_subscription_keys,
                                                   metrics_computation_config=metrics_computation_config,
                                                   loss_computation_config=loss_computation_config,
                                                   show_progress=show_progress
                                                   )
        train_component = constructable.construct()

        assert isinstance(train_component, EvalComponent)
