from itertools import chain
from typing import Iterable, List, Callable
from ml_gym.loss_functions.loss_functions import Loss
from ml_gym.models.nn.net import NNModel
from ml_gym.data_handling.dataset_loader import DatasetLoader
import torch
from ml_gym.batching.batch import DatasetBatch
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.optimizers.optimizer import OptimizerAdapter
from ml_gym.gym.post_processing import PredictPostProcessingIF
import numpy as np


class TrainComponent(StatefulComponent):
    """
    TrainComponent class used when there is only one CPU or GPU to train model.
    """

    def __init__(self, inference_component: InferenceComponent, post_processors: List[PredictPostProcessingIF],
                 loss_fun: Loss):
        self.loss_fun = loss_fun
        self.inference_component = inference_component
        self.post_processors = post_processors

    def _train_batch(self, batch: DatasetBatch, model: NNModel, optimizer: OptimizerAdapter, device: torch.device):
        """
        Train torch NN Model with a batch.

        :params:
               batch (DatasetBatch): Train Dataset
               model (NNModel): Torch Neural Network module.
               optimizer (OptimizerAdapter): Object of OptimizerAdapter used to initaite optimizer for model.
               device (torch.device): Torch device either CPUs or a specified GPU.

        :returns:
            model (NNModel): Torch Neural Network module.
        """
        model = model.to(device)
        batch.to(device)
        model.zero_grad()
        loss = self.calc_loss(model, batch)
        loss.sum().backward()
        optimizer.step()
        return model

    @staticmethod
    def _prepare_data_loader_stack(dataloader: DatasetLoader, num_epochs: int, initial_epoch: int,
                                   num_batches_per_epoch: int) -> Iterable:

        current_batch_index = (initial_epoch * num_batches_per_epoch) % len(dataloader)
        skip_num_dataloaders = int((initial_epoch * num_batches_per_epoch) / len(dataloader))

        num_total_batches = num_batches_per_epoch*num_epochs  # number of total batches irrespective of the warm start
        num_dataloaders = int(np.ceil(num_total_batches/len(dataloader))) - skip_num_dataloaders

        data_loaders = chain(*([dataloader]*num_dataloaders))
        data_loader_iterable = iter(zip(range(num_total_batches), data_loaders))

        # fast forward to the batch index that we left off in case of a warm start
        for _ in range(current_batch_index):
            next(data_loader_iterable)
        return data_loader_iterable

    def train(self, model: NNModel, optimizer: OptimizerAdapter, dataloader: DatasetLoader, device: torch.device,
              batch_done_callback_fun: Callable, epoch_done_callback_fun: Callable,
              num_epochs: int, initial_epoch: int,  num_batches_per_epoch: int = None) -> NNModel:
        """
        Train torch NN Model.

        :params:
               model (NNModel): Torch Neural Network module.
               optimizer (OptimizerAdapter): Object of OptimizerAdapter used to initaite optimizer for model.
               dataloader (DatasetLoader): Obhect of DatasetLoader used to load Data to be trained on.
               device (torch.device): Torch device either CPUs or a specified GPU.
               batch_done_callback_fun (Callable): Batch number for which details to be logged.
               epoch_done_callback_fun (Callable): numner of batches to be trained.
               num_epochs (int): Number of epochs to be trained.
               initial_epoch (int): Initial epoch number.
               num_batches_per_epoch (int): number of batches to be trained per epoch.

        :returns:
            model (NNModel): Torch Neural Network module.
        """
        model.train()
        num_batches_per_epoch = num_batches_per_epoch if num_batches_per_epoch is not None else len(dataloader)
        dataloader_iterable = TrainComponent._prepare_data_loader_stack(dataloader=dataloader,
                                                                        num_epochs=num_epochs,
                                                                        initial_epoch=initial_epoch,
                                                                        num_batches_per_epoch=num_batches_per_epoch)

        for batch_id, batch in dataloader_iterable:
            current_epoch = initial_epoch + int(batch_id / num_batches_per_epoch)
            model = self._train_batch(batch=batch, model=model, optimizer=optimizer, device=device)

            batch_done_callback_fun(status="train",
                                    num_batches=num_batches_per_epoch,
                                    current_batch=batch_id % num_batches_per_epoch,
                                    splits=[dataloader.dataset_tag],
                                    current_split=dataloader.dataset_tag,
                                    num_epochs=num_epochs,
                                    current_epoch=current_epoch)

            if (batch_id + 1) % num_batches_per_epoch == 0:  # when epoch done
                epoch_done_callback_fun(num_epochs=num_epochs, current_epoch=current_epoch, model=model)
                model.train()

        return model

    def calc_loss(self, model: NNModel, batch: DatasetBatch) -> torch.Tensor:
        """
        Valvulate loss given the loss function.

        :params:
               model (NNModel): Torch Neural Network module
               batch (DatasetBatch); Batch of data for which loss is to be calcualted.

        :returns:
            loss (List[torch.Tensor]): Loss list for batch.
        """
        forward_batch = self.inference_component.predict(batch=batch, model=model, post_processors=self.post_processors)
        loss = self.loss_fun(forward_batch)
        return loss


class Trainer:
    """
    Trainer class contains functions used to train the torch Neural Net model on CPU.
    """

    def __init__(self, train_component: TrainComponent, train_loader: DatasetLoader):
        self.train_component = train_component
        self.train_loader = train_loader

    def train(self, num_epochs: int, model: NNModel, optimizer: OptimizerAdapter, device: torch.device,
              batch_done_callback_fun: Callable, epoch_done_callback: Callable, initial_epoch: int,
              num_batches_per_epoch: int = None) -> NNModel:
        """
        Train torch NN Model.

        :params:
               num_epochs (int): Number of epochs to be trained.
               model (NNModel): Torch Neural Network module.
               optimizer (OptimizerAdapter): Object of OptimizerAdapter used to initaite optimizer for model.
               device (torch.device): Torch device either CPUs or a specified GPU.
               batch_done_callback_fun (Callable): Batch number for which details to be logged.
               epoch_done_callback (Callable): numner of batches to be trained.
               initial_epoch (int): Initial epoch number.
               num_batches_per_epoch (int): number of batches to be trained per epoch.

        :returns:
            model (NNModel): Torch Neural Network module.
        """

        model = self.train_component.train(model=model, optimizer=optimizer, dataloader=self.train_loader, device=device,
                                           batch_done_callback_fun=batch_done_callback_fun, epoch_done_callback_fun=epoch_done_callback,
                                           num_epochs=num_epochs, num_batches_per_epoch=num_batches_per_epoch, initial_epoch=initial_epoch)
        return model
