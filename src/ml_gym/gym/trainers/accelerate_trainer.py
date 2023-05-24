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
    """
    AccelerateTrainComponent class used when there are multiple GPUs to train model.
    """
    def __init__(self, inference_component: InferenceComponent, post_processors: List[PredictPostProcessingIF],
                 loss_fun: Loss):
        self.loss_fun = loss_fun
        self.inference_component = inference_component
        self.post_processors = post_processors

    def _train_batch(self, accelerator: Accelerator, batch: DatasetBatch, model: NNModel, optimizer: OptimizerAdapter) -> NNModel:
        """
        Train torch NN Model with a batch.

        :params:
           - batch (DatasetBatch): Train Dataset.
           - model (NNModel): Torch Neural Network module.
           - optimizer (OptimizerAdapter): Object of OptimizerAdapter used to initaite optimizer for model.
           - device (torch.device): Torch device either CPUs or a specified GPU.

        :returns:
            model (NNModel): Torch Neural Network module.
        """
        model.zero_grad()
        loss = self.calc_loss(model, batch).sum()

        # if accelerator.is_main_process:
        #     w = model.module.fc_layers[0].weight
        #     print(f"\n\nBefore Update main thread: {w}")
        #     accelerator.backward(loss)
        #     optimizer.step()
        #     w = model.module.fc_layers[0].weight
        #     print(f"\n\nAfter Update main thread: {w}")
        # else:
        #     w = model.module.fc_layers[0].weight
        #     print(f"\n\nBefore 2nd thread: {w}")
        #     accelerator.backward(loss)
        #     optimizer.step()
        #     w = model.module.fc_layers[0].weight
        #     print(f"\n\nAfter 2nd thread: {w}")
        #     print("\n")

        accelerator.backward(loss)
        optimizer.step()

        return model

    def train(self, model: NNModel, optimizer: OptimizerAdapter, dataloader: DatasetLoader,
              accelerator: Accelerator, batch_done_callback_fun: Callable, epoch_done_callback_fun: Callable,
              num_epochs: int, num_batches_per_epoch: int = None) -> NNModel:
        """
        Train torch NN Model.

        :params:
           - model (NNModel): Torch Neural Network module.
           - optimizer (OptimizerAdapter): Object of OptimizerAdapter used to initaite optimizer for model.
           - dataloader (DatasetLoader): Obhect of DatasetLoader used to load Data to be trained on.
           - accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.
           - batch_done_callback_fun (Callable): Batch number for which details to be logged.
           - epoch_done_callback_fun (Callable): numner of batches to be trained.
           - num_epochs(int): number of epochs to be trained to.
           - num_batches_per_epoch (int): numner of batches to be trained per epoch.

        :returns:
            model (NNModel): Torch Neural Network module.
        """

        model.train()

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
                                        splits=[dataloader.dataset_tag],
                                        current_split=dataloader.dataset_tag,
                                        num_epochs=num_epochs,
                                        current_epoch=current_epoch)
            if (batch_id + 1) % num_batches_per_epoch == 0:  # when epoch done
                epoch_done_callback_fun(num_epochs=num_epochs, current_epoch=current_epoch, model=model, accelerator=accelerator)
                model.train()
        return model

    def calc_loss(self, model: NNModel, batch: DatasetBatch) -> torch.Tensor:
        """
        Valvulate loss given the loss function.

        :params:
           - model (NNModel): Torch Neural Network module.
           - batch (DatasetBatch); Batch of data for which loss is to be calcualted.

        :returns:
            loss (List[torch.Tensor]): Loss list for batch.
        """
        forward_batch = self.inference_component.predict(batch=batch, model=model, post_processors=self.post_processors)
        loss = self.loss_fun(forward_batch)
        return loss


class AccelerateTrainer:
    """
    Trainer class contains functions used to train the torch Neural Net model on GPU
    """
    def __init__(self, train_component: AccelerateTrainComponent, train_loader: DatasetLoader):
        self.train_component = train_component
        self.train_loader = train_loader

    def train(self, num_epochs: int, model: NNModel, optimizer: OptimizerAdapter,
              batch_done_callback_fun: Callable, epoch_done_callback: Callable, accelerator: Accelerator,
              num_batches_per_epoch: int = None) -> NNModel:
        """
        Train torch NN Model.

        :params:
           - num_epochs (int): Number of epochs to be trained.
           - model (NNModel): Torch Neural Network module.
           - optimizer (OptimizerAdapter): Object of OptimizerAdapter used to initaite optimizer for model.
           - batch_done_callback_fun (Callable): Batch number for which details to be logged.
           - epoch_done_callback (Callable): numner of batches to be trained.
           - accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.
           - num_batches_per_epoch (int): number of batches to be trained per epoch.
           
        :returns:
            model (NNModel): Torch Neural Network module.
        """

        # accelerate_train_loader = accelerator.prepare(self.train_loader)

        model = self.train_component.train(model=model, optimizer=optimizer, dataloader=self.train_loader, accelerator=accelerator,
                                           batch_done_callback_fun=batch_done_callback_fun, epoch_done_callback_fun=epoch_done_callback,
                                           num_epochs=num_epochs, num_batches_per_epoch=num_batches_per_epoch)
        return model
