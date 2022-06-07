#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
===========================================
    @Project : mlgym 
    @Author  : Xiangyu Zeng
    @Date    : 6/7/22 9:06 PM 
    @Description    :
        
===========================================
"""
from typing import Dict, List

import pytest

from ml_gym.blueprints.constructables import TrainComponentConstructable, LossFunctionRegistryConstructable, \
    PredictionPostProcessingRegistryConstructable, Requirement, TrainerConstructable, DataLoadersConstructable, \
    MetricFunctionRegistryConstructable, EvalComponentConstructable
from ml_gym.gym.evaluator import EvalComponent
from ml_gym.gym.post_processing import ArgmaxPostProcessorImpl
from ml_gym.gym.trainer import TrainComponent
from ml_gym.loss_functions.loss_functions import CrossEntropyLoss

from test_data_loader_constructable import CollatorFixture


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


class TestTrainComponentConstructable(RegistryFixture):
    def test_constructable(self, prediction_postprocessing_registry, loss_function_registry):
        requirements = {
            "prediction_postprocessing_registry": Requirement(components=prediction_postprocessing_registry),
            "loss_function_registry": Requirement(components=loss_function_registry)}
        loss_fun_config: Dict = {"key": "CrossEntropyLoss", "target_subscription_key": "target_key",
                                 "prediction_subscription_key": "model_prediction_key"}
        post_processors_config: List[Dict] = [
            {"key": "ARG_MAX",
             "params": {"prediction_subscription_key": "model_prediction_key_anchor",
                        "prediction_publication_key": "postprocessing_argmax_key_anchor"}}]

        show_progress: bool = False
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


class TestEvalComponentConstructable(RegistryFixture, DataLoaderFixture):
    def test_constructable(self, data_loader, prediction_postprocessing_registry, loss_function_registry,
                           metric_registry):
        train_split_name: str = "train"
        metrics_config: List = [{"key": "F1_SCORE",
                                 "params": {"average": "macro"},
                                 "prediction_subscription_key": "model_prediction_key",
                                 "target_subscription_key": "target_key",
                                 "tag": "F1_SCORE_macro"}]
        loss_funs_config: List = [
            {"prediction_subscription_key": "model_prediction_key",
             "target_subscription_key": "target_key",
             "key": "CrossEntropyLoss",
             "tag": "cross_entropy_loss"}]
        post_processors_config: List = [{
            "key": "ARG_MAX",
            "prediction_subscription_key": "model_prediction_key",
            "prediction_publication_key": "postprocessing_argmax_key"
        }]
        show_progress: bool = False
        cpu_target_subscription_keys: List[str] = ["target_key"]
        cpu_prediction_subscription_keys: List[str] = ["postprocessing_argmax_key", "model_prediction_key"]
        metrics_computation_config: List[Dict] = None
        loss_computation_config: List[Dict] = None

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
