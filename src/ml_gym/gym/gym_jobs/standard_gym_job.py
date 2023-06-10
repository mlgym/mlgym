from io import BytesIO
from ml_gym.early_stopping.early_stopping_strategies import EarlyStoppingIF
from ml_gym.gym.gym_jobs.gym_job import AbstractGymJob
from ml_gym.models.nn.net import NNModel
from ml_gym.gym.evaluators.evaluator import Evaluator
from ml_gym.gym.trainers.standard_trainer import Trainer
from ml_gym.modes import RunMode
from ml_gym.optimizers.lr_schedulers import LRSchedulerAdapter
from ml_gym.optimizers.optimizer import OptimizerAdapter
import torch
from typing import List
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.persistency.logging import ExperimentStatusLogger
from functools import partial
from ml_gym.persistency.io import GridSearchAPIClientIF, CheckpointResource
import pickle
from ml_gym.checkpointing.checkpointing import CheckpointingIF
from ml_gym.error_handling.exception import EarlyStoppingCriterionFulfilledError


class StandardGymJob(AbstractGymJob):
    """
    Standard Gym Job class used for running job on single CPU or GPU.
    """

    def __init__(self, experiment_status_logger: ExperimentStatusLogger, gs_api_client: GridSearchAPIClientIF,
                 grid_search_id: str, experiment_id: int, run_mode: RunMode, num_epochs: int,
                 model: NNModel, optimizer: OptimizerAdapter, trainer: Trainer, evaluator: Evaluator,
                 checkpointing_strategy: CheckpointingIF, early_stopping_strategy: EarlyStoppingIF = None,
                 warm_start_epoch: int = 0, lr_scheduler: LRSchedulerAdapter = None, num_batches_per_epoch: int = None):
        super().__init__(experiment_status_logger=experiment_status_logger, gs_api_client=gs_api_client, grid_search_id=grid_search_id,
                         experiment_id=experiment_id, run_mode=run_mode, num_epochs=num_epochs, model=model, optimizer=optimizer,
                         trainer=trainer, evaluator=evaluator, checkpointing_strategy=checkpointing_strategy,
                         early_stopping_strategy=early_stopping_strategy, warm_start_epoch=warm_start_epoch, lr_scheduler=lr_scheduler,
                         num_batches_per_epoch=num_batches_per_epoch)

    def execute(self, device: torch.device):
        """ Executes the job

        :params:
            device (torch.device): torch device either CPUs or a specified GPU
        """
        self._execution_method(device)
        self._experiment_status_logger.disconnect()

    def _train_step(self, device: torch.device) -> NNModel:
        """ 
        Training the model.

        :params:
            device (torch.device): torch device either CPUs or a specified GPU
        :returns:
            model (NNModel): Neural Net torch model. 
        """
        partial_batch_processed_callback = partial(AbstractGymJob.batch_processed_callback, num_epochs=self.num_epochs,
                                                   experiment_status_logger=self._experiment_status_logger)
        model = self.trainer.train_epoch(self.model, self.optimizer, device,
                                         batch_processed_callback_fun=partial_batch_processed_callback)
        return model

    def _evaluation_step(self, current_epoch: int, device: torch.device) -> List[EvaluationBatchResult]:
        """ 
        Evaluating the model.

        :params:
               current_epoch (int): Current epoch number for cerating checkpoints.
               device (torch.device): torch device either CPUs or a specified GPU

        :returns:
            evaluation_results (EvaluationBatchResult): Object storing entire evaluation infotmation.
        """
        partial_batch_processed_callback = partial(AbstractGymJob.batch_processed_callback, num_epochs=self.num_epochs,
                                                   current_epoch=current_epoch,
                                                   experiment_status_logger=self._experiment_status_logger)
        partial_epoch_result_callback = partial(self.epoch_result_callback, experiment_status_logger=self._experiment_status_logger,
                                                current_epoch=current_epoch)

        evaluation_results = self.evaluator.evaluate(model=self.model,
                                                     device=device,
                                                     batch_processed_callback_fun=partial_batch_processed_callback,
                                                     epoch_result_callback_fun=partial_epoch_result_callback)

        return evaluation_results

    def _execute_train(self, device: torch.device, initial_epoch: int = 0):
        """ 
        Execute training of the model.

        :params:
            device (torch.device): torch device either CPUs or a specified GPU
        """
        self.optimizer.register_model_params(model_params=dict(self.model.named_parameters()))
        self.lr_scheduler.register_optimizer(optimizer=self.optimizer)

        partial_batch_done_callback = partial(self.batch_processed_callback, experiment_status_logger=self._experiment_status_logger)
        def evaluation_step_routine(current_epoch: int): return self._evaluation_step(device=device, current_epoch=current_epoch)
        partial_train_epoch_done_callback = partial(self.train_epoch_done_callback, evaluation_step_routine=evaluation_step_routine)

        try:
            model = self.trainer.train(num_epochs=self.num_epochs, model=self.model, optimizer=self.optimizer, device=device,
                                       batch_done_callback_fun=partial_batch_done_callback,
                                       epoch_done_callback=partial_train_epoch_done_callback,
                                       num_batches_per_epoch=self.num_batches_per_epoch,
                                       initial_epoch=initial_epoch)
        except EarlyStoppingCriterionFulfilledError:
            print("Early stopping criterion matched. Stopping training.")

    def _execute_warm_start(self, device: torch.device):
        """ 
        Execute warm start of the model from an epoch.

        :params:
               device (torch.device): torch device either CPUs or a specified GPU.
               warm_start_epoch (int): Epoch to start Training from.
        """

        if self.warm_start_epoch > -1:
            model_state_buffer = BytesIO(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                    experiment_id=self.experiment_id,
                                                                                    checkpoint_id=self.warm_start_epoch,
                                                                                    checkpoint_resource=CheckpointResource.model))
            model_state = torch.load(model_state_buffer, map_location=device)
            self.model.load_state_dict(model_state)
            model_state_buffer.close()

            self.model = self.model.to(device)

            optimizer_state_buffer = BytesIO(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                        experiment_id=self.experiment_id,
                                                                                        checkpoint_id=self.warm_start_epoch,
                                                                                        checkpoint_resource=CheckpointResource.optimizer))
            optimizer_state = torch.load(optimizer_state_buffer, map_location=device)
            self.optimizer.load_state_dict(optimizer_state)
            optimizer_state_buffer.close()

            lr_scheduler_state_buffer = BytesIO(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                           experiment_id=self.experiment_id,
                                                                                           checkpoint_id=self.warm_start_epoch,
                                                                                           checkpoint_resource=CheckpointResource.lr_scheduler))
            lr_scheduler_state = torch.load(lr_scheduler_state_buffer, map_location=device)
            self.lr_scheduler.load_state_dict(lr_scheduler_state)
            lr_scheduler_state_buffer.close()

            stateful_component_state = pickle.loads(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                               experiment_id=self.experiment_id,
                                                                                               checkpoint_id=self.warm_start_epoch,
                                                                                               checkpoint_resource=CheckpointResource.stateful_components))
            print(stateful_component_state)
            self.set_state(stateful_component_state)

        self._execute_train(device, initial_epoch=self.warm_start_epoch)
