#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import pytest
from data_stack.repository.repository import DatasetRepository
from ml_gym.blueprints.constructables import Requirement, DataCollatorConstructable, DataLoadersConstructable, \
    DatasetIteratorConstructable, DeprecatedDataLoadersConstructable
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.data_handling.postprocessors.collator import Collator
from torch.utils.data import RandomSampler, WeightedRandomSampler, SequentialSampler

import torch
from typing import List, Dict
import tempfile
import shutil

from mocked_classes import MockedMNISTFactory, MockedCollator


class IteratorFixtures:
    @pytest.fixture
    def tmp_folder_path(self) -> str:
        path = tempfile.mkdtemp()
        yield path
        shutil.rmtree(path)

    @pytest.fixture
    def repository(self):
        dataset_repository: DatasetRepository = DatasetRepository()
        dataset_repository.register("mnist", MockedMNISTFactory())
        return dataset_repository

    @pytest.fixture
    def repository_requirement(self, repository) -> Dict[str, Requirement]:
        return {"repository": Requirement(components=repository)}

    @pytest.fixture
    def informed_iterators(self, repository_requirement):
        constructable = DatasetIteratorConstructable(component_identifier="iterator_component",
                                                     requirements=repository_requirement,
                                                     dataset_identifier="mnist",
                                                     split_configs=[{"split": "train"}, {"split": "test"}])
        iterators = constructable.construct()
        return iterators


class CollatorFixture(IteratorFixtures):
    @pytest.fixture
    def collator_type(self):
        return MockedCollator

    @pytest.fixture
    def data_collator(self, informed_iterators, collator_type):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}
        collator_params = {}
        collator_type = collator_type
        constructable = DataCollatorConstructable(component_identifier="data_collator_component",
                                                  requirements=requirements,
                                                  collator_params=collator_params,
                                                  collator_type=collator_type)
        data_collator = constructable.construct()
        return data_collator


class TestDataLoadersConstructable(CollatorFixture):
    @pytest.mark.parametrize("sampling_strategies, drop_last, batch_size, sampler_class",
                             [
                                 ({'train': {"strategy": "RANDOM", "seed": 0}}, True, 16, RandomSampler),
                                 ({"train": {"strategy": "WEIGHTED_RANDOM", "label_pos": 2, "seed": 0}}, False, 32,
                                  WeightedRandomSampler),
                                 ({"train": {"strategy": "IN_ORDER"}}, True, 32, SequentialSampler),
                             ])
    def test_constructable(self, sampling_strategies, drop_last, batch_size, sampler_class, informed_iterators,
                           data_collator):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"]),
                        "data_collator": Requirement(components=data_collator, subscription=["train", "test"])}
        constructable = DataLoadersConstructable(component_identifier="data_loader_component",
                                                 requirements=requirements,
                                                 batch_size=batch_size,
                                                 sampling_strategies=sampling_strategies,
                                                 drop_last=drop_last
                                                 )
        data_loader = constructable.construct()
        assert isinstance(data_loader["train"], DatasetLoader)
        assert isinstance(data_loader["test"], DatasetLoader)
        assert data_loader["train"].batch_size == batch_size
        assert data_loader["test"].batch_size == batch_size
        assert data_loader["train"].drop_last == drop_last
        assert data_loader["test"].drop_last == drop_last
        assert isinstance(data_loader["train"].sampler, sampler_class)


class TestDeprecatedDataLoadersConstructable(CollatorFixture):
    @pytest.mark.parametrize("weigthed_sampling_split_name, sample_class",
                             [
                                 ("train", WeightedRandomSampler),
                                 ("test", WeightedRandomSampler)
                             ])
    def test_constructable(self, informed_iterators, data_collator, weigthed_sampling_split_name, sample_class):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"]),
                        "data_collator": Requirement(components=data_collator, subscription=["train", "test"])}
        batch_size: int = 1
        label_pos: int = 2
        drop_last: bool = False
        seeds: Dict = {'train': 0, 'test': 0}
        constructable = DeprecatedDataLoadersConstructable(component_identifier="data_loader_component",
                                                           requirements=requirements,
                                                           weigthed_sampling_split_name=weigthed_sampling_split_name,
                                                           batch_size=batch_size,
                                                           seeds=seeds,
                                                           label_pos=label_pos,
                                                           drop_last=drop_last
                                                           )
        data_loader = constructable.construct()
        assert isinstance(data_loader["train"], DatasetLoader)
        assert isinstance(data_loader["test"], DatasetLoader)

        assert isinstance(data_loader[weigthed_sampling_split_name].sampler, sample_class)


class TestDataCollatorConstructable(CollatorFixture):
    def test_constructable(self, informed_iterators, collator_type):
        requirements = {"iterators": Requirement(components=informed_iterators, subscription=["train", "test"])}
        collator_params = {}
        collator_type = collator_type
        constructable = DataCollatorConstructable(component_identifier="data_collator_constructable",
                                                  requirements=requirements,
                                                  collator_params=collator_params,
                                                  collator_type=collator_type)
        data_collator = constructable.construct()
        assert isinstance(data_collator, collator_type)
