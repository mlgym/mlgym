from itertools import chain
from typing import Dict, List, Callable, Any
from ml_gym.gym.trainers.standard_trainer import TrainComponent, TrainerIF
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.models.nn.net import NNModel
from ml_gym.data_handling.dataset_loader import DatasetLoader, GeneratorLMDatasetLoader
import torch
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.optimizers.optimizer import OptimizerAdapter
import tqdm
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.error_handling.exception import ModelAlreadyFullyTrainedError, TrainingStateCorruptError
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
        num_dataloaders = np.ceil(num_total_batches/len(dataloader))
        data_loaders = chain([dataloader]*num_dataloaders)

        for batch_id, batch in zip(range(num_total_batches), data_loaders):
            if batch_id % num_batches_per_epoch == 0:  # when epoch done
                current_epoch = int(batch_id / num_batches_per_epoch)
                epoch_done_callback_fun(num_epochs=num_epochs, current_epoch=current_epoch, model=model)

            model = self._train_batch(accelerator=accelerator, batch=batch, model=model, optimizer=optimizer)

            batch_done_callback_fun(status="train",
                                    num_batches=num_batches_per_epoch,
                                    current_batch=batch_id % num_batches_per_epoch,
                                    splits=[dataloader.dataset_tag],
                                    current_split=dataloader.dataset_tag)

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

        accelerate_train_loader = accelerator.prepare(self.train_loader)

        model = self.train_component.train(model=model, optimizer=optimizer, dataloaer=accelerate_train_loader, accelerator=accelerator,
                                           batch_done_callback_fun=batch_done_callback_fun, epoch_done_callback_fun=epoch_done_callback,
                                           num_epochs=num_epochs, num_batches_per_epoch=num_batches_per_epoch)
        return model


# class LMTrainer(AccelerateTrainer):
#     """ Language Model Trainer
#     Language models are generally trained using datasets of tremendous size, making the concept of "epochs" meaningless, as we tend to not iterate
#     over the entire dataset multiple times. In this class, we set an epoch to be a subset of the entire dataset, e.g., 1000 batches.
#     As a result, the first epoch consists of the first 1k batches in the dataset and the second epoch of the baches from position 1000 to 2000, and so on.
#     This gives us the opportunity to calculate the validation loss scores after each epoch and track the training progress.

#     """

#     def __init__(self, train_component: TrainComponent, train_loader: DatasetLoader, num_batches_per_epoch: int):
#         super().__init__(train_component=train_component, train_loader=train_loader)
#         self.num_batches_per_epoch = num_batches_per_epoch

#     def set_current_epoch(self, epoch: int):
#         if self.num_epochs is None:
#             raise TrainingStateCorruptError("Variable num_epochs must be set before setting current_epoch.")
#         self.current_epoch = epoch

#         self.train_loader_generator = GeneratorLMDatasetLoader(data_loader=self.train_loader,
#                                                                num_batches_per_epoch=self.num_batches_per_epoch,
#                                                                num_epochs=self.num_epochs,
#                                                                current_epoch=self.current_epoch)

#     def train_epoch(self, model: NNModel, optimizer: OptimizerAdapter, device: torch.device,
#                     batch_processed_callback_fun: Callable = None) -> NNModel:
#         if self.accelerator is None:
#             raise TrainingStateCorruptError("Accelerator not initialized in trainer.")
#         if self.current_epoch > self.num_epochs:
#             raise ModelAlreadyFullyTrainedError(f"Model has been already trained for {self.current_epoch}/{self.num_epochs} epochs.")
#         model = self.train_component.train_epoch(model, optimizer, self.train_loader_generator, device, self.current_epoch,
#                                                  batch_processed_callback_fun)
#         self.current_epoch += 1
#         return model
