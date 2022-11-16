#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest
from ml_gym.blueprints.constructables import Requirement, EvalComponentConstructable, EvaluatorConstructable
from ml_gym.gym.evaluator import Evaluator
from pytests.blueprints.constructables.test_eval_component_constructable import EvalConfigFixture
from pytests.blueprints.constructables.test_train_component_constructable import RegistryFixture, DataLoaderFixture


class EvalComponentFixture(RegistryFixture, DataLoaderFixture, EvalConfigFixture):
    @pytest.fixture
    def eval_component(self, data_loader, prediction_postprocessing_registry, loss_function_registry,
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
        eval_component = constructable.construct()
        return eval_component


class TestEvaluatorConstructable(EvalComponentFixture):
    def test_constructable(self, data_loader, eval_component):
        requirements = {
            "data_loaders": Requirement(components=data_loader),
            "eval_component": Requirement(components=eval_component)}
        constructable = EvaluatorConstructable(component_identifier="eval_constructable",
                                               requirements=requirements
                                               )
        evaluator = constructable.construct()
        assert isinstance(evaluator, Evaluator)