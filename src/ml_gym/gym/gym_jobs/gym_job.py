from abc import abstractmethod
from typing import Callable, List
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.checkpointing.checkpointing import CheckpointingIF, CheckpointingInstruction
from ml_gym.early_stopping.early_stopping_strategies import EarlyStoppingIF
from ml_gym.error_handling.exception import EarlyStoppingCriterionFulfilledError
from ml_gym.gym.evaluators.evaluator import Evaluator
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.gym.trainers.standard_trainer import Trainer
from ml_gym.models.nn.net import NNModel
from ml_gym.modes import RunMode
from ml_gym.optimizers.lr_scheduler_factory import LRSchedulerFactory
from ml_gym.optimizers.lr_schedulers import LRSchedulerAdapter
from ml_gym.optimizers.optimizer import OptimizerAdapter
from ml_gym.persistency.io import GridSearchAPIClientIF
from ml_gym.persistency.logging import ExperimentStatusLogger
import torch
from accelerate import Accelerator


class AbstractGymJob(StatefulComponent):

    def __init__(self, experiment_status_logger: ExperimentStatusLogger, gs_api_client: GridSearchAPIClientIF,
                 grid_search_id: str, experiment_id: int, run_mode: RunMode, num_epochs: int,
                 model: NNModel, optimizer: OptimizerAdapter, trainer: Trainer, evaluator: Evaluator,
                 checkpointing_strategy: CheckpointingIF, early_stopping_strategy: EarlyStoppingIF = None,
                 warm_start_epoch: int = 0, lr_scheduler: LRSchedulerAdapter = None, num_batches_per_epoch: int = None):
        super().__init__()
        # logging
        self._experiment_status_logger = experiment_status_logger
        self.gs_api_client = gs_api_client

        # identifiers
        self.grid_search_id = grid_search_id
        self.experiment_id = experiment_id

        # configuration
        self.run_mode = run_mode
        self.num_epochs = num_epochs
        self.num_batches_per_epoch = num_batches_per_epoch
        self.warm_start_epoch = warm_start_epoch
        if run_mode == RunMode.TRAIN:
            self._execution_method = self._execute_train
        elif run_mode == RunMode.WARM_START:
            self._execution_method = self._execute_warm_start
        else:
            raise NotImplementedError

        # components
        self.model = model
        self.optimizer = optimizer
        self.lr_scheduler = lr_scheduler if lr_scheduler is not None else LRSchedulerFactory.get_lr_scheduler("dummy")
        self.evaluator = evaluator
        self.trainer = trainer

        self.checkpointing_strategy = checkpointing_strategy
        self.early_stopping_strategy = early_stopping_strategy

    @abstractmethod
    def execute(self, device: torch.device):
        raise NotImplementedError

    def run_checkpointing(self, checkpoint_instruction: CheckpointingInstruction, current_epoch: int):
        """
        Create and delete checkpoints for each epoch in experiments.

        :params:
            checkpoint_instruction: CheckpointingInstruction object
        """

        if checkpoint_instruction.save_current:
            payload_dict = {
                "epoch": current_epoch,
                "model": self.model.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "lr_scheduler": self.lr_scheduler.state_dict(),
                "stateful_components": self.get_state(),
            }

            self.gs_api_client.add_checkpoint_resource(
                grid_search_id=self.grid_search_id, experiment_id=self.experiment_id, payload=payload_dict
            )

        for epoch in checkpoint_instruction.checkpoints_to_delete:
            self.gs_api_client.delete_checkpoint_resource(grid_search_id=self.grid_search_id, experiment_id=self.experiment_id, epoch=epoch)

    @staticmethod
    def batch_processed_callback(status: str, experiment_status_logger: ExperimentStatusLogger, num_batches: int,
                                 current_batch: int, splits: List[str], current_split: str, num_epochs: int, current_epoch: int):
        if (current_batch % max(1, int(num_batches/10))) == 0:  # TODO make update period configurable
            experiment_status_logger.log_experiment_status(status=status,
                                                           num_epochs=num_epochs,
                                                           current_epoch=current_epoch,
                                                           splits=splits,
                                                           current_split=current_split,
                                                           num_batches=num_batches,
                                                           current_batch=current_batch)

    @staticmethod
    def epoch_result_callback(experiment_status_logger: ExperimentStatusLogger, evaluation_result: EvaluationBatchResult,
                              current_epoch: int):
        experiment_status_logger.log_evaluation_results(evaluation_result, current_epoch)

    def train_epoch_done_callback(self, num_epochs: int, current_epoch: int, model: NNModel, evaluation_step_routine: Callable,
                                  accelerator: Accelerator = None):
        evaluation_results = evaluation_step_routine(current_epoch=current_epoch)
        if current_epoch > 0:
            self.lr_scheduler.step()
        if accelerator is not None and accelerator.is_main_process:
            checkpointing_instruction = self.checkpointing_strategy.get_model_checkpoint_instruction(num_epochs=num_epochs,
                                                                                                     current_epoch=current_epoch,
                                                                                                     evaluation_result=evaluation_results)
            self.run_checkpointing(checkpointing_instruction, current_epoch=current_epoch)
        if self.early_stopping_strategy.is_stopping_criterion_fulfilled(current_epoch=current_epoch,
                                                                        evaluation_results=evaluation_results):
            raise EarlyStoppingCriterionFulfilledError

    def _evaluation_step(self, device: torch.device) -> List[EvaluationBatchResult]:
        raise NotImplementedError
