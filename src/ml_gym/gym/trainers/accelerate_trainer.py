from itertools import chain
from typing import List, Callable
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.models.nn.net import NNModel
from ml_gym.data_handling.dataset_loader import DatasetLoader
import torch
from ml_gym.batching.batch import DatasetBatch
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.optimizers.optimizer import OptimizerAdapter
from ml_gym.gym.post_processing import PredictPostProcessingIF
from accelerate import Accelerator
import numpy as np


class AccelerateTrainComponent(StatefulComponent):
    def __init__(self, inference_component: InferenceComponent, post_processors: List[PredictPostProcessingIF],
                 loss_fun: Loss):
        self.loss_fun = loss_fun
        self.inference_component = inference_component
        self.post_processors = post_processors

    def _train_batch(self, accelerator: Accelerator, batch: DatasetBatch, model: NNModel, optimizer: OptimizerAdapter) -> NNModel:
        model.zero_grad()
        loss = self.calc_loss(model, batch).sum()
        accelerator.backward(loss)
        optimizer.step()
        return model

    def train(self, model: NNModel, optimizer: OptimizerAdapter, dataloader: DatasetLoader,
              accelerator: Accelerator, batch_done_callback_fun: Callable, epoch_done_callback_fun: Callable,
              num_epochs: int, num_batches_per_epoch: int = None) -> NNModel:

        if num_batches_per_epoch is None:
            num_batches_per_epoch = len(dataloader)

        num_total_batches = num_batches_per_epoch*num_epochs
        num_dataloaders = int(np.ceil(num_total_batches/len(dataloader)))
        data_loaders = chain(*([dataloader]*num_dataloaders))

        for batch_id, batch in zip(range(num_total_batches), data_loaders):
            current_epoch = int(batch_id / num_batches_per_epoch)
            model = self._train_batch(accelerator=accelerator, batch=batch, model=model, optimizer=optimizer)
            if accelerator.is_main_process:
                batch_done_callback_fun(status="train",
                                        num_batches=num_batches_per_epoch,
                                        current_batch=batch_id % num_batches_per_epoch,
                                        splits=[],  # TODO needs to be set properly
                                        current_split="",  # TODO needs to be set properly
                                        num_epochs=num_epochs,
                                        current_epoch=current_epoch)
            if (batch_id + 1) % num_batches_per_epoch == 0:  # when epoch done
                epoch_done_callback_fun(num_epochs=num_epochs, current_epoch=current_epoch, model=model)

        return model

    def calc_loss(self, model: NNModel, batch: DatasetBatch) -> torch.Tensor:
        forward_batch = self.inference_component.predict(batch=batch, model=model, post_processors=self.post_processors)
        loss = self.loss_fun(forward_batch)
        return loss


class AccelerateTrainer:
    def __init__(self, train_component: AccelerateTrainComponent, train_loader: DatasetLoader):
        self.train_component = train_component
        self.train_loader = train_loader

    def train(self, num_epochs: int, model: NNModel, optimizer: OptimizerAdapter,
              batch_done_callback_fun: Callable, epoch_done_callback: Callable, accelerator: Accelerator,
              num_batches_per_epoch: int = None) -> NNModel:

        model = model.train()

        # accelerate_train_loader = accelerator.prepare(self.train_loader)

        model = self.train_component.train(model=model, optimizer=optimizer, dataloader=self.train_loader, accelerator=accelerator,
                                           batch_done_callback_fun=batch_done_callback_fun, epoch_done_callback_fun=epoch_done_callback,
                                           num_epochs=num_epochs, num_batches_per_epoch=num_batches_per_epoch)
        return model
