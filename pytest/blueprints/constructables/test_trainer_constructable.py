#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from typing import List, Dict

import pytest

from test_train_component_constructable import RegistryFixture, DataLoaderFixture
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


class TestTrainerConstructable(TrainComponentFixture, DataLoaderFixture):
    def test_constructable(self, data_loader, train_component):
        requirements = {
            "data_loaders": Requirement(components=data_loader),
            "train_component": Requirement(components=train_component)}
        constructable = TrainerConstructable(component_identifier="trainer_constructable",
                                             requirements=requirements
                                             )
        trainer = constructable.construct()
        return trainer

