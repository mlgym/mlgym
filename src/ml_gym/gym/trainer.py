from abc import abstractmethod
from typing import Dict, List, Callable, Any
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


class TrainComponent(StatefulComponent):
    def __init__(self, inference_component: InferenceComponent, post_processors: List[PredictPostProcessingIF],
                 loss_fun: Loss, show_progress: bool = False):
        self.loss_fun = loss_fun
        self.inference_component = inference_component
        self.post_processors = post_processors
        self.show_progress = show_progress

    def train_batch(self, batch: DatasetBatch, model: NNModel, optimizer: OptimizerAdapter, device: torch.device):
        model = model.to(device)
        batch.to_device(device)
        model.zero_grad()
        loss = self.calc_loss(model, batch)
        loss.sum().backward()
        optimizer.step()

    def train_epoch(self, model: NNModel, optimizer: OptimizerAdapter, data_loader: DatasetLoader,
                    device: torch.device, epoch: int, batch_processed_callback_fun: Callable = None) -> NNModel:
        self.map_batches(fun=self.train_batch,
                         loader=data_loader,
                         fun_params={"device": device,
                                     "model": model,
                                     "optimizer": optimizer},
                         progress_info=f"Training {data_loader.dataset_name}  @epoch {epoch}",
                         callback_fun=batch_processed_callback_fun)
        return model

    def calc_loss(self, model: NNModel, batch: DatasetBatch) -> torch.Tensor:
        forward_batch = self.inference_component.predict(batch=batch, model=model, post_processors=self.post_processors)
        loss = self.loss_fun(forward_batch)
        return loss

    @staticmethod
    def map_batches(fun: Callable[[DatasetBatch, NNModel], Any], loader: DatasetLoader,
                    fun_params: Dict[str, Any] = None, progress_info: str = None,
                    callback_fun: Callable = None) -> List[InferenceResultBatch]:
        """
        Applies a function to each dataset_batch within a DatasetLoader
        """
        num_batches = len(loader)
        processed_batches = 0
        update_lag = max(1, int(num_batches/10))
        fun_params = fun_params if fun_params is not None else dict()
        result = []
        if progress_info is not None:
            for dataset_batch in tqdm.tqdm(loader, desc=progress_info):
                result.append(fun(dataset_batch, **fun_params))
                processed_batches += 1
                if callback_fun is not None and (processed_batches % update_lag == 0 or processed_batches == num_batches):
                    callback_fun(status="train",
                                 num_batches=num_batches,
                                 current_batch=processed_batches,
                                 splits=[loader.dataset_tag],
                                 current_split=loader.dataset_tag)
        else:
            for dataset_batch in loader:
                result.append(fun(dataset_batch, **fun_params))
                processed_batches += 1
                if callback_fun is not None and (processed_batches % update_lag == 0 or processed_batches == num_batches):
                    callback_fun(status="train",
                                 num_batches=num_batches,
                                 current_batch=processed_batches,
                                 splits=[loader.dataset_tag],
                                 current_split=loader.dataset_tag)
        return result


class TrainerIF(StatefulComponent):

    @abstractmethod
    def is_done(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def set_num_epochs(self, num_epochs: int):
        raise NotImplementedError

    @abstractmethod
    def set_current_epoch(self, epoch: int):
        raise NotImplementedError


class Trainer(TrainerIF):
    def __init__(self, train_component: TrainComponent, train_loader: DatasetLoader, verbose=False):
        self.train_component = train_component
        self.train_loader = train_loader
        self.verbose = verbose
        self.current_epoch = 1
        self.num_epochs = -1

    def is_done(self) -> bool:
        return self.current_epoch > self.num_epochs  # training starts at epoch 1, epoch 0 is just for evaluation, therefore >

    def set_num_epochs(self, num_epochs: int):
        self.num_epochs = num_epochs

    def set_current_epoch(self, epoch: int):
        self.current_epoch = epoch

    def train_epoch(self, model: NNModel, optimizer: OptimizerAdapter, device: torch.device,
                    batch_processed_callback_fun: Callable = None) -> NNModel:
        if self.current_epoch > self.num_epochs:
            raise ModelAlreadyFullyTrainedError(f"Model has been already trained for {self.current_epoch}/{self.num_epochs} epochs.")
        self.train_loader.device = device
        model = self.train_component.train_epoch(model, optimizer, self.train_loader, device, self.current_epoch,
                                                 batch_processed_callback_fun)
        self.current_epoch += 1
        return model


class LMTrainer(TrainerIF):
    """ Language Model Trainer
    Language models are generally trained using datasets of tremendous size, making the concept of "epochs" meaningless, as we tend to not iterate
    over the entire dataset multiple times. In this class, we set an epoch to be a subset of the entire dataset, e.g., 1000 batches.
    As a result, the first epoch consists of the first 1k batches in the dataset and the second epoch of the baches from position 1000 to 2000, and so on. 
    This gives us the opportunity to calculate the validation loss scores after each epoch and track the training progress.  

    """

    def __init__(self, train_component: TrainComponent, train_loader: DatasetLoader, num_batches_per_epoch: int, verbose=False):
        self.train_component = train_component
        self.train_loader = train_loader
        self.verbose = verbose
        self.current_epoch = 1
        self.num_epochs = None
        self.num_batches_per_epoch = num_batches_per_epoch

    def is_done(self) -> bool:
        return self.current_epoch > self.num_epochs  # training starts at epoch 1, epoch 0 is just for evaluation, therefore >

    def set_num_epochs(self, num_epochs: int):
        self.num_epochs = num_epochs

    def set_current_epoch(self, epoch: int):
        if self.num_epochs is None:
            raise TrainingStateCorruptError("Variable num_epochs must be set before setting current_epoch.")
        self.current_epoch = epoch

        self.train_loader_generator = GeneratorLMDatasetLoader(data_loader=self.train_loader,
                                                               num_batches_per_epoch=self.num_batches_per_epoch,
                                                               num_epochs=self.num_epochs,
                                                               current_epoch=self.current_epoch)

    def train_epoch(self, model: NNModel, optimizer: OptimizerAdapter, device: torch.device,
                    batch_processed_callback_fun: Callable = None) -> NNModel:
        if self.current_epoch > self.num_epochs:
            raise ModelAlreadyFullyTrainedError(f"Model has been already trained for {self.current_epoch}/{self.num_epochs} epochs.")
        model = self.train_component.train_epoch(model, optimizer, self.train_loader_generator, device, self.current_epoch,
                                                 batch_processed_callback_fun)
        self.current_epoch += 1
        return model
