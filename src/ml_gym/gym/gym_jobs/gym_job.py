from abc import abstractmethod
import io
import os
import pickle
from typing import Callable, List
from ml_board.backend.restful_api.data_models import CheckpointResource
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
import shutil
import tempfile


class AbstractGymJob(StatefulComponent):
    """
    Class contating all running and config information for Gym Job.
    """

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

    def run_checkpointing(self, checkpoint_instruction: CheckpointingInstruction, current_epoch: int, accelerator: Accelerator = None):
        """
        Create and delete checkpoints for each epoch in experiments.

        :params:
           - checkpoint_instruction (CheckpointingInstruction): CheckpointingInstruction object.
           - current_epoch (int): Current epoch number for cerating checkpoints.
        """
        if checkpoint_instruction.save_current:

            if accelerator is not None:
                global_rank = accelerator.process_index
                # TODO replace with an in-memory file system solution
                with tempfile.TemporaryDirectory() as tmpdirname:
                    root_dir = os.path.join(tmpdirname, f"epoch_{current_epoch}/rank_{global_rank}")
                    checkpoint_file_name = f"checkpoint_rank_{global_rank}"
                    checkpoint_path = os.path.join(root_dir, f"rank_{global_rank}/")
                    accelerator.save_state(output_dir=checkpoint_path)
                    shutil.make_archive(base_name=os.path.join(root_dir, checkpoint_file_name), format='zip', root_dir=checkpoint_path)
                    with open(os.path.join(root_dir, f"{checkpoint_file_name}.zip"), 'rb') as fd:
                        self.gs_api_client.add_checkpoint_resource(grid_search_id=self.grid_search_id, experiment_id=self.experiment_id,
                                                                   epoch=current_epoch, payload_stream=fd,
                                                                   custom_file_name=f"{checkpoint_file_name}.zip")

            else:
                model_buffer = io.BytesIO()
                torch.save(self.model.state_dict(), model_buffer)

                optimizer_buffer = io.BytesIO()
                torch.save(self.optimizer.state_dict(), optimizer_buffer)

                lr_scheduler_buffer = io.BytesIO()
                torch.save(self.lr_scheduler.state_dict(), lr_scheduler_buffer)

                payload_dict = {
                    CheckpointResource.model: model_buffer.getvalue(),
                    CheckpointResource.optimizer: optimizer_buffer.getvalue(),
                    CheckpointResource.lr_scheduler: lr_scheduler_buffer.getvalue(),
                    CheckpointResource.stateful_components: pickle.dumps(self.get_state())
                }

                for checkpoint_resource_key, checkpoint_resource_stream in payload_dict.items():
                    self.gs_api_client.add_checkpoint_resource(grid_search_id=self.grid_search_id, experiment_id=self.experiment_id,
                                                               epoch=current_epoch, payload_stream=checkpoint_resource_stream,
                                                               custom_file_name=checkpoint_resource_key)
                model_buffer.close()
                optimizer_buffer.close()
                lr_scheduler_buffer.close()

        if accelerator is None or accelerator is not None and accelerator.is_main_process:
            for epoch in checkpoint_instruction.checkpoints_to_delete:
                self.gs_api_client.delete_checkpoints(grid_search_id=self.grid_search_id, experiment_id=self.experiment_id, epoch=epoch)

    @staticmethod
    def batch_processed_callback(status: str, experiment_status_logger: ExperimentStatusLogger, num_batches: int,
                                 current_batch: int, splits: List[str], current_split: str, num_epochs: int, current_epoch: int):
        """
        Log experiment details for processed batch of data.

        :params:
           - status (str): CheckpointingInstruction object.
           - experiment_status_logger (ExperimentStatusLogger): Epoch/Experiment number for cerating checkpoints.
           - num_batches (int): numner of batches to be trained.
           - current_batch (int): Batch number for which details to be logged.
           - splits (List[str]): Splits list for the data
           - current_split (str): Current split of the data.
           - num_epochs(int): number of epochs to be trained to.
           - current_epoch (int): Current epoch number.
        """
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
        """
        Log evaluation details for an epoch.

        :params:
           - experiment_status_logger (ExperimentStatusLogger): Epoch/Experiment number for cerating checkpoints.
           - evaluation_result (EvaluationBatchResult): Object storing entire epoch infotmation.
           - current_epoch (int): Current epoch number.
        """
        experiment_status_logger.log_evaluation_results(evaluation_result, current_epoch)

    def train_epoch_done_callback(self, num_epochs: int, current_epoch: int, model: NNModel, evaluation_step_routine: Callable,
                                  accelerator: Accelerator = None):
        """
        Log evaluation details for an epoch.

        :params:
           - num_epochs (int): Number of epochs to be trained.
           - current_epoch (int): Current epoch number.
           - model (NNModel): Torch Neural Network module.
           - evaluation_step_routine (Callable): Epoch/Experiment number for cerating checkpoints.
           - accelerator (Accelerator): Accelerator object used for distributed training over multiple GPUs.
        """
        evaluation_results = evaluation_step_routine(current_epoch=current_epoch)
        if current_epoch > 0:
            self.lr_scheduler.step()
        checkpointing_instruction = self.checkpointing_strategy.get_model_checkpoint_instruction(num_epochs=num_epochs,
                                                                                                 current_epoch=current_epoch,
                                                                                                 evaluation_result=evaluation_results)
        self.run_checkpointing(checkpointing_instruction, current_epoch=current_epoch, accelerator=accelerator)

        if self.early_stopping_strategy.is_stopping_criterion_fulfilled(current_epoch=current_epoch,
                                                                        evaluation_results=evaluation_results):
            raise EarlyStoppingCriterionFulfilledError

    def _evaluation_step(self, device: torch.device) -> List[EvaluationBatchResult]:
        raise NotImplementedError
