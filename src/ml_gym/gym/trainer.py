from typing import Dict, List, Callable, Any
from ml_gym.loss_functions.loss_functions import Loss, LossWarmupMixin
from ml_gym.models.nn.net import NNModel
from ml_gym.data_handling.dataset_loader import DatasetLoader
import torch
from ml_gym.batch import InferenceResultBatch, DatasetBatch, Batch
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.gym.stateful_components import StatefulComponent
from torch.optim.optimizer import Optimizer


class TrainComponent(StatefulComponent):
    def __init__(self, inference_component: InferenceComponent, loss_fun: Loss):
        self.loss_fun = loss_fun
        self.inference_component = inference_component

    def train_batch(self, batch: DatasetBatch, model: NNModel, optimizer: Optimizer, device: torch.device):
        model.zero_grad()
        batch.to_device(device)
        loss = self.calc_loss(model, batch)
        loss.sum().backward()
        optimizer.step()

    def train_epoch(self, model: NNModel, optimizer: Optimizer, data_loader: DatasetLoader,
                    device: torch.device) -> NNModel:
        self.map_batches(fun=self.train_batch,
                         loader=data_loader,
                         fun_params={"device": device,
                                     "model": model,
                                     "optimizer": optimizer})
        return model

    def warm_up(self, model: NNModel, data_loader: DatasetLoader, device: torch.device):
        def init_loss(loss_fun: Loss, batch: InferenceResultBatch):
            if isinstance(loss_fun, LossWarmupMixin):
                loss_fun.warm_up(batch)
                loss_fun.finish_warmup()
        with torch.no_grad():
            prediction_batches = self.map_batches(fun=self.forward_batch,
                                                  fun_params={"device": device, "model": model},
                                                  loader=data_loader)
        prediction_batch = InferenceResultBatch.combine(prediction_batches)
        init_loss(self.loss_fun, prediction_batch)

    def forward_batch(self, batch: DatasetBatch, model: NNModel, device: torch.device) -> InferenceResultBatch:
        model.to(device)
        batch.to_device(device)
        forward_result_batch = self.inference_component.predict(model, batch)
        return forward_result_batch

    def calc_loss(self, model: NNModel, batch: DatasetBatch) -> torch.Tensor:
        forward_batch = self.inference_component.predict(model, batch)
        loss = self.loss_fun(forward_batch)
        return loss

    @staticmethod
    def map_batches(fun: Callable[[DatasetBatch, NNModel], Any], loader: DatasetLoader,
                    fun_params: Dict[str, Any] = None) -> List[Batch]:
        """
        Applies a function to each batch within a DatasetLoader
        """
        # TODO: This loads the entire dataset into memory.
        # We should make this a generator instead to prevent memory overflows.
        # Also code duplication with evaluator
        fun_params = fun_params if fun_params is not None else dict()
        return [fun(batch, **fun_params) for batch in loader]


class Trainer(StatefulComponent):
    def __init__(self, train_component: TrainComponent, train_loader: DatasetLoader, verbose=False):
        self.train_component = train_component
        self.train_loader = train_loader
        self.verbose = verbose

    def warm_up(self, model: NNModel, device: torch.device):
        self.train_component.warm_up(model, self.train_loader, device)

    def train_epoch(self, model: NNModel, optimizer: Optimizer, device: torch.device) -> NNModel:
        model = self.train_component.train_epoch(model, optimizer, self.train_loader, device)
        return model
