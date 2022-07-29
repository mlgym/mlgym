from copy import deepcopy
from typing import List

import pytest
import torch
from ml_gym.batching.batch import DatasetBatch
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.gym.trainer import TrainComponent, Trainer
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.models.nn.net import NNModel
from ml_gym.optimizers.optimizer import OptimizerAdapter
from torch.optim.sgd import SGD
from torch.utils.data import DataLoader

from pytests.test_env.component_fixtures import ModelFixture, LossFixture, Postprocessors, DataLoaderFixture, \
    MockedDataCollatorFixture


class TestTrainerComponent(ModelFixture, LossFixture, Postprocessors, DataLoaderFixture, MockedDataCollatorFixture):

    @pytest.fixture
    def device(self) -> torch.device:
        return torch.device(0)

    @pytest.fixture
    def show_progress(self) -> bool:
        return True

    @pytest.fixture
    def epoch(self) -> int:
        return 1

    @pytest.fixture
    def test_batch(self, data_loader: DatasetLoader, device: torch.device) -> DatasetBatch:
        dataset_batch = list(data_loader)[0]
        dataset_batch.to_device(device=device)
        return dataset_batch

    @pytest.fixture
    def optimizer(self) -> OptimizerAdapter:
        optimizer = OptimizerAdapter(SGD, {"lr": 1.0, "momentum": 0.9})
        return optimizer

    @pytest.fixture
    def inference_component(self) -> InferenceComponent:
        inference_component = InferenceComponent(no_grad=False)
        return inference_component

    @pytest.fixture
    def test_train_component(self, inference_component: InferenceComponent, postprocessors: List[PredictPostProcessingIF],
                        train_loss_fun: Loss, show_progress: bool) -> TrainComponent:
        train_component = TrainComponent(inference_component, postprocessors, train_loss_fun, show_progress)

        return train_component

    # def test_train_batch(self, train_component: TrainComponent, batch: DatasetBatch, model: NNModel,
    #                      optimizer: OptimizerAdapter, device: torch.device):
    #     optimizer.register_model_params(dict(model.named_parameters()))
    #
    #     old_model_parameters = deepcopy(dict(model.named_parameters()))

        # train_component.train_batch(batch, model, optimizer, device)
        #
        # model_parameters = dict(model.named_parameters())
        #
        # for old_key, old_value in old_model_parameters.items():
        #     for key, value in model_parameters.items():
        #         if old_key == key:
        #             assert not (old_value.detach().cpu().numpy() == value.detach().cpu().numpy()).all()

    # def test_train_epoch(self, train_component: TrainComponent, data_loader: DatasetLoader, model: NNModel,
    #                      optimizer: OptimizerAdapter, device: torch.device, epoch: int):
    #
    #     optimizer.register_model_params(dict(model.named_parameters()))
    #
    #     old_model_parameters = deepcopy(dict(model.named_parameters()))
    #
    #     train_component.train_epoch(model, optimizer, data_loader, device, epoch)
    #
    #     model_parameters = dict(model.named_parameters())
    #
    #     for old_key, old_value in old_model_parameters.items():
    #         for key, value in model_parameters.items():
    #             if old_key == key:
    #                 assert not (old_value.detach().cpu().numpy() == value.detach().cpu().numpy()).all()


class TestTrainer(TestTrainerComponent):
    @pytest.fixture
    def trainer(self, train_component: TrainComponent, data_loader: DatasetLoader) -> Trainer:
        trainer = Trainer(train_component, data_loader)
        return trainer

    @pytest.fixture
    def cur_epoch(self) -> int:
        return 1

    # def test_trainer_epoch(self, trainer: Trainer, cur_epoch: int, epoch: int, model: NNModel,
    #                        optimizer: OptimizerAdapter, device: torch.device):
    #
    #     old_model_parameters = deepcopy(dict(model.named_parameters()))
    #
    #     optimizer.register_model_params(dict(model.named_parameters()))
    #
    #     trainer.set_current_epoch(1)
    #     trainer.set_num_epochs(epoch)
    #     for i in range(epoch):
    #         model = trainer.train_epoch(model, optimizer, device)
    #     assert trainer.is_done()
    #
    #     model_parameters = dict(model.named_parameters())
    #     # check if the model parameters changed
    #     for old_key, old_value in old_model_parameters.items():
    #         for key, value in model_parameters.items():
    #             if old_key == key:
    #                 assert not (old_value.detach().cpu().numpy() == value.detach().cpu().numpy()).all()
