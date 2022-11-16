#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest
from ml_gym.gym.trainer import Trainer
from pytests.blueprints.constructables.test_train_component_constructable import RegistryFixture, DataLoaderFixture, TrainConfigFixture
from ml_gym.blueprints.constructables import Requirement, TrainerConstructable,  \
    TrainComponentConstructable


class TrainComponentFixture(RegistryFixture, TrainConfigFixture):
    @pytest.fixture
    def train_component(self, prediction_postprocessing_registry, loss_function_registry, loss_fun_config,
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
        assert isinstance(trainer, Trainer)
