from typing import Dict, List

import pytest
import torch
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from data_stack.dataset.meta import MetaFactory
from ml_gym.data_handling.dataset_loader import DatasetLoader, SamplerFactory
from ml_gym.data_handling.postprocessors.collator import Collator
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.loss_functions.loss_factory import LossFactory
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.models.nn.net import NNModel
from torch.utils.data import DataLoader, Sampler

from pytests.test_env.linear_net_blueprint import LinearNet, MockedDatasetFactory, MockedDataCollator


class Keys:
    @pytest.fixture
    def model_prediction_key_anchor(self):
        return "model_prediction_key"

    @pytest.fixture
    def postprocessing_key_anchor(self):
        return "postprocessing_key"

    @pytest.fixture
    def target_key_anchor(self):
        return "target_key"


class ModelFixture(Keys):
    @pytest.fixture
    def seed(self):
        return 0

    @pytest.fixture
    def layer_config(self) -> List[Dict]:
        return [{"params": {"in_features": 1, "out_features": 128}, "type": "fc"},
                {"params": {"in_features": 128, "out_features": 1}, "type": "fc"}]

    @pytest.fixture
    def prediction_publication_key(self, model_prediction_key_anchor):
        return model_prediction_key_anchor

    @pytest.fixture
    def model(self, prediction_publication_key: str, layer_config: Dict, device: torch.device,
              seed: int = 0) -> NNModel:
        model = LinearNet(prediction_publication_key, layer_config, seed).to(device)
        return model


class Postprocessors(Keys):
    @pytest.fixture
    def postprocessors(self) -> List[PredictPostProcessingIF]:
        return []


class LossFixture(Keys):
    @pytest.fixture
    def target_subscription_key(self, target_key_anchor):
        return target_key_anchor

    @pytest.fixture
    def prediction_subscription_key(self, model_prediction_key_anchor):
        return model_prediction_key_anchor

    @pytest.fixture
    def train_loss_fun(self, target_subscription_key: str, prediction_subscription_key: str) -> Loss:
        loss_func = LossFactory.get_lp_loss(target_subscription_key, prediction_subscription_key)
        return loss_func


class DataLoaderFixture(Keys):
    @pytest.fixture
    def batch_size(self) -> int:
        return 16

    @pytest.fixture
    def sampler(self, dataset_iterator) -> Sampler:
        sampler = SamplerFactory.get_random_sampler(dataset_iterator, seed=0)
        return sampler

    @pytest.fixture
    def drop_last(self) -> bool:
        return True

    @pytest.fixture
    def dataset_iterator(self) -> InformedDatasetIteratorIF:
        config = {"split": "train"}
        dataset_iterator, iterator_meta = MockedDatasetFactory().get_dataset_iterator(config)
        meta = MetaFactory.get_dataset_meta(identifier="dataset id",
                                            dataset_name="dataset",
                                            dataset_tag="full",
                                            iterator_meta=iterator_meta)
        iterator = InformedDatasetFactory.get_dataset_iterator(dataset_iterator, meta)
        return iterator

    # @pytest.fixture
    def test_data_loader(self, dataset_iterator: InformedDatasetIteratorIF, batch_size: int, sampler: Sampler,
                    collator: Collator, drop_last: bool = False) -> DataLoader:
        data_loader = DatasetLoader(dataset_iterator=dataset_iterator,
                                    batch_size=batch_size,
                                    sampler=sampler,
                                    collate_fn=collator,
                                    drop_last=drop_last)
        return data_loader


class MockedDataCollatorFixture(Keys):
    @pytest.fixture
    def target_publication_key(self, target_key_anchor) -> str:
        return target_key_anchor

    @pytest.fixture
    def collator(self, target_publication_key) -> Collator:
        collator = MockedDataCollator(target_publication_key=target_publication_key)
        return collator

