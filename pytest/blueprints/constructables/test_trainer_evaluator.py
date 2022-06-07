#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
===========================================
    @Project : mlgym 
    @Author  : Xiangyu Zeng
    @Date    : 6/8/22 12:19 AM 
    @Description    :
        
===========================================
"""
from typing import List, Dict

import pytest

from test_train_eval_component_constructable import RegistryFixture, DataLoaderFixture
from ml_gym.blueprints.constructables import Requirement, TrainerConstructable, EvalComponentConstructable, \
    TrainComponentConstructable, EvaluatorConstructable


class TrainComponentFixture(RegistryFixture):
    @pytest.fixture
    def train_component(self, prediction_postprocessing_registry, loss_function_registry):
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
        return train_component


class EvalComponentFixture(RegistryFixture, DataLoaderFixture):
    @pytest.fixture
    def eval_component(self, data_loader, prediction_postprocessing_registry, loss_function_registry,
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
        return train_component


class TestTrainerConstructable(TrainComponentFixture):
    def test_constructable(self, data_loader, train_component):
        requirements = {
            "data_loaders": Requirement(components=data_loader),
            "train_component": Requirement(components=train_component)}
        constructable = TrainerConstructable(component_identifier="trainer_constructable",
                                             requirements=requirements
                                             )
        trainer = constructable.construct()
        return trainer


class TestEvaluatorConstructable(EvalComponentFixture):
    def test_constructable(self, data_loader, eval_component):
        requirements = {
            "data_loaders": Requirement(components=data_loader),
            "eval_component": Requirement(components=eval_component)}
        constructable = EvaluatorConstructable(component_identifier="eval_constructable",
                                               requirements=requirements
                                               )
        trainer = constructable.construct()
        return trainer
