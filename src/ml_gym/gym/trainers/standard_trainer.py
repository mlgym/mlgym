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
import numpy as np
import tqdm


class TrainComponent(StatefulComponent):
    def __init__(self, inference_component: InferenceComponent, post_processors: List[PredictPostProcessingIF],
                 loss_fun: Loss):
        self.loss_fun = loss_fun
        self.inference_component = inference_component
        self.post_processors = post_processors

    def _train_batch(self, batch: DatasetBatch, model: NNModel, optimizer: OptimizerAdapter, device: torch.device):
        model = model.to(device)
        batch.to_device(device)
        model.zero_grad()
        loss = self.calc_loss(model, batch)
        loss.sum().backward()
        optimizer.step()
        return model

    def train(self, model: NNModel, optimizer: OptimizerAdapter, dataloader: DatasetLoader, device: torch.device,
              batch_done_callback_fun: Callable, epoch_done_callback_fun: Callable,
              num_epochs: int, num_batches_per_epoch: int = None) -> NNModel:

        if num_batches_per_epoch is None:
            num_batches_per_epoch = len(dataloader)

        num_total_batches = num_batches_per_epoch*num_epochs
        num_dataloaders = int(np.ceil(num_total_batches/len(dataloader)))
        data_loaders = chain(*([dataloader]*num_dataloaders))
        train_bar = tqdm.tqdm(total=num_batches_per_epoch)

        for batch_id, batch in zip(range(num_total_batches), data_loaders):
            if batch_id % num_batches_per_epoch == 0:  # when epoch done
                current_epoch = int(batch_id / num_batches_per_epoch)
                epoch_done_callback_fun(num_epochs=num_epochs, current_epoch=current_epoch, model=model)
                train_bar.n = 0
                train_bar.refresh()
                train_bar.desc = f"Training epoch {current_epoch}"
            if batch_id % 100 == 0:
                train_bar.update(100)
                train_bar.refresh()

            model = self._train_batch(batch=batch, model=model, optimizer=optimizer, device=device)

            batch_done_callback_fun(status="train",
                                    num_batches=num_batches_per_epoch,
                                    current_batch=batch_id % num_batches_per_epoch,
                                    splits=[dataloader.dataset_tag],
                                    current_split=dataloader.dataset_tag,
                                    num_epochs=num_epochs,
                                    current_epoch=current_epoch)

        train_bar.close()
        return model

    def calc_loss(self, model: NNModel, batch: DatasetBatch) -> torch.Tensor:
        forward_batch = self.inference_component.predict(batch=batch, model=model, post_processors=self.post_processors)
        loss = self.loss_fun(forward_batch)
        return loss


class Trainer:
    def __init__(self, train_component: TrainComponent, train_loader: DatasetLoader):
        self.train_component = train_component
        self.train_loader = train_loader
        self.current_epoch = 1
        self.num_epochs = -1

    def train(self, num_epochs: int, model: NNModel, optimizer: OptimizerAdapter, device: torch.device,
              batch_done_callback_fun: Callable, epoch_done_callback: Callable,
              num_batches_per_epoch: int = None) -> NNModel:

        model = self.train_component.train(model=model, optimizer=optimizer, dataloader=self.train_loader, device=device,
                                           batch_done_callback_fun=batch_done_callback_fun, epoch_done_callback_fun=epoch_done_callback,
                                           num_epochs=num_epochs, num_batches_per_epoch=num_batches_per_epoch)
        return model
