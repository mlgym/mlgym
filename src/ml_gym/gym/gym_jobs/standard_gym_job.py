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
from ml_gym.checkpointing.checkpointing import CheckpointingIF, CheckpointingInstruction


class StandardGymJob(AbstractGymJob):

    def __init__(self, experiment_status_logger: ExperimentStatusLogger, gs_api_client: GridSearchAPIClientIF,
                 grid_search_id: str, experiment_id: int, run_mode: RunMode, num_epochs: int,
                 model: NNModel, optimizer: OptimizerAdapter, trainer: Trainer, evaluator: Evaluator,
                 checkpointing_strategy: CheckpointingIF, early_stopping_strategy: EarlyStoppingIF = None,
                 warm_start_epoch: int = 0, lr_scheduler: LRSchedulerAdapter = None):
        super().__init__(experiment_status_logger=experiment_status_logger, gs_api_client=gs_api_client, grid_search_id=grid_search_id,
                         experiment_id=experiment_id, run_mode=run_mode, num_epochs=num_epochs, model=model, optimizer=optimizer,
                         trainer=trainer, evaluator=evaluator, checkpointing_strategy=checkpointing_strategy,
                         early_stopping_strategy=early_stopping_strategy, warm_start_epoch=warm_start_epoch, lr_scheduler=lr_scheduler)

    def execute(self, device: torch.device):
        """ Executes the job

        Args:
            device: torch device either CPUs or a specified GPU
        """
        self._execution_method(device)
        self._experiment_status_logger.disconnect()

    def _train_step(self, device: torch.device) -> NNModel:
        partial_batch_processed_callback = partial(self.batch_processed_callback, num_epochs=self.num_epochs,
                                                   current_epoch=self.current_epoch,
                                                   experiment_status_logger=self._experiment_status_logger)
        model = self.trainer.train_epoch(self.model, self.optimizer, device,
                                         batch_processed_callback_fun=partial_batch_processed_callback)
        return model

    def _evaluation_step(self, device: torch.device) -> List[EvaluationBatchResult]:
        self.model.to(device)
        partial_batch_processed_callback = partial(self.batch_processed_callback, num_epochs=self.num_epochs,
                                                   current_epoch=self.current_epoch,
                                                   experiment_status_logger=self._experiment_status_logger)
        partial_epoch_result_callback = partial(self.epoch_result_callback, current_epoch=self.current_epoch,
                                                experiment_status_logger=self._experiment_status_logger)

        evaluation_results = self.evaluator.evaluate(model=self.model,
                                                     device=device,
                                                     current_epoch=self.current_epoch,
                                                     num_epochs=self.num_epochs,
                                                     batch_processed_callback_fun=partial_batch_processed_callback,
                                                     epoch_result_callback_fun=partial_epoch_result_callback)

        return evaluation_results

    def run_checkpointing(self, checkpoint_instruction: CheckpointingInstruction):
        # TODO use self.gs_api_client to make the calls. Note that some of the endpoints are also still missing for that...

        pass
        # if checkpoint_instruction.save_current:
        #     self._experiment_status_logger.log_checkpoint(epoch=self.current_epoch,
        #                                                   model_state_dict=self.model.state_dict(),
        #                                                   optimizer_state_dict=self.optimizer.state_dict(),
        #                                                   lr_scheduler_state_dict=self.lr_scheduler.state_dict(),
        #                                                   stateful_components_state_dict=self.get_state())
        # for epoch in checkpoint_instruction.checkpoints_to_delete:
        #     print(f"epoch to delete: {epoch}")
        #     self._experiment_status_logger.log_checkpoint(epoch=epoch,
        #                                                   model_state_dict=None,
        #                                                   optimizer_state_dict=None,
        #                                                   lr_scheduler_state_dict=None,
        #                                                   stateful_components_state_dict=None)

    def _execute_train(self, device: torch.device):
        self.optimizer.register_model_params(model_params=dict(self.model.named_parameters()))
        self.lr_scheduler.register_optimizer(optimizer=self.optimizer)

        self.trainer.set_num_epochs(num_epochs=self.num_epochs)

        # initial evaluation
        evaluation_results = self._evaluation_step(device)

        # we store the initial model / last warmup model again
        checkpointing_instruction = self.checkpointing_strategy.get_model_checkpoint_instruction(num_epochs=self.num_epochs,
                                                                                                 current_epoch=self.current_epoch,
                                                                                                 evaluation_result=evaluation_results)
        self.run_checkpointing(checkpointing_instruction)

        # if early stopping criterion is fulfilled we can stop the training progress
        if self.early_stopping_strategy.is_stopping_criterion_fulfilled(current_epoch=self.current_epoch,
                                                                        evaluation_results=evaluation_results):
            return

        partial_batch_done_callback = partial(self.batch_processed_callback, experiment_status_logger=self._experiment_status_logger)
        model = self.trainer.train(num_epochs=self.num_epochs, model=self.model, optimizer=self.optimizer,
                                   batch_done_callback_fun=partial_batch_done_callback,
                                   epoch_done_callback=self.train_epoch_done_callback,
                                   num_batches_per_epoch=self.num_batches_per_epoch)

    def _execute_warm_start(self, device: torch.device):
        if self.current_epoch > 0:
            model_state = pickle.loads(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                  experiment_id=self.experiment_id,
                                                                                  checkpoint_id=self.current_epoch,
                                                                                  checkpoint_resource=CheckpointResource.model))
            self.model.load_state_dict(model_state)

            optimizer_state = pickle.loads(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                      experiment_id=self.experiment_id,
                                                                                      checkpoint_id=self.current_epoch,
                                                                                      checkpoint_resource=CheckpointResource.optimizer))
            self.optimizer.load_state_dict(optimizer_state)

            lr_scheduler_state = pickle.loads(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                         experiment_id=self.experiment_id,
                                                                                         checkpoint_id=self.current_epoch,
                                                                                         checkpoint_resource=CheckpointResource.lr_scheduler))
            self.lr_scheduler.load_state_dict(lr_scheduler_state)

            stateful_component_state = pickle.loads(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                               experiment_id=self.experiment_id,
                                                                                               checkpoint_id=self.current_epoch,
                                                                                               checkpoint_resource=CheckpointResource.stateful_components))
            self.set_state(stateful_component_state)

        self._execute_train(device)
