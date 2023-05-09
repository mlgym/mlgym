from ml_gym.data_handling.dataset_loader import DatasetLoaderFactory
from ml_gym.early_stopping.early_stopping_strategies import EarlyStoppingIF
from ml_gym.gym.gym_jobs.gym_job import AbstractGymJob
from ml_gym.gym.trainers.accelerate_trainer import AccelerateTrainer
from ml_gym.models.nn.net import NNModel
from ml_gym.gym.evaluators.evaluator import Evaluator
from ml_gym.modes import RunMode
from ml_gym.optimizers.lr_schedulers import LRSchedulerAdapter
from ml_gym.optimizers.optimizer import OptimizerAdapter
from typing import List
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.persistency.logging import ExperimentStatusLogger
from functools import partial
from ml_gym.persistency.io import GridSearchAPIClientIF, CheckpointResource
import pickle
from ml_gym.checkpointing.checkpointing import CheckpointingIF
from accelerate import Accelerator


class AccelerateGymJob(AbstractGymJob):
    """
    Accelerate Gym Job class used for running job on multiple GPUs.
    """

    def __init__(self, experiment_status_logger: ExperimentStatusLogger, gs_api_client: GridSearchAPIClientIF,
                 grid_search_id: str, experiment_id: int, run_mode: RunMode, num_epochs: int,
                 model: NNModel, optimizer: OptimizerAdapter, trainer: AccelerateTrainer, evaluator: Evaluator,
                 checkpointing_strategy: CheckpointingIF, accelerator: Accelerator, early_stopping_strategy: EarlyStoppingIF = None,
                 warm_start_epoch: int = 0, lr_scheduler: LRSchedulerAdapter = None, num_batches_per_epoch: int = None):
        super().__init__(experiment_status_logger=experiment_status_logger, gs_api_client=gs_api_client, grid_search_id=grid_search_id,
                         experiment_id=experiment_id, run_mode=run_mode, num_epochs=num_epochs, model=model, optimizer=optimizer,
                         trainer=trainer, evaluator=evaluator, checkpointing_strategy=checkpointing_strategy,
                         early_stopping_strategy=early_stopping_strategy, warm_start_epoch=warm_start_epoch, lr_scheduler=lr_scheduler,
                         num_batches_per_epoch=num_batches_per_epoch)
        self.num_batches_per_epoch = num_batches_per_epoch
        self.accelerator = accelerator

    def execute(self):
        """ Executes the job

        """
        self._execution_method()
        self._experiment_status_logger.disconnect()

    def _evaluation_step(self, current_epoch: int) -> List[EvaluationBatchResult]:
        """ 
        Evaluating the model.

        :params:
            current_epoch (int): Current epoch number for cerating checkpoints.
        :returns:
            evaluation_results (List[EvaluationBatchResult]): Object storing entire evaluation infotmation.
        """
        partial_batch_processed_callback = partial(self.batch_processed_callback, num_epochs=self.num_epochs,
                                                   current_epoch=current_epoch,
                                                   experiment_status_logger=self._experiment_status_logger)
        partial_epoch_result_callback = partial(self.epoch_result_callback, current_epoch=current_epoch,
                                                experiment_status_logger=self._experiment_status_logger)

        evaluation_results = self.evaluator.evaluate(model=self.model,
                                                     accelerator=self.accelerator,
                                                     batch_processed_callback_fun=partial_batch_processed_callback,
                                                     epoch_result_callback_fun=partial_epoch_result_callback)

        return evaluation_results

    def _execute_train(self):
        """ 
        Execute training of the model.
        """
        self.optimizer.register_model_params(model_params=dict(self.model.named_parameters()))
        self.lr_scheduler.register_optimizer(optimizer=self.optimizer)

        self.model, self.optimizer, self.trainer, self.evaluator, self.lr_scheduler, train_loader = self.accelerator.prepare(self.model,
                                                                                                                             self.optimizer,
                                                                                                                             self.trainer,
                                                                                                                             self.evaluator,
                                                                                                                             self.lr_scheduler,
                                                                                                                             self.trainer.train_loader)
        self.trainer.train_loader = DatasetLoaderFactory.get_data_loader_shard_wrapper(data_loader_shard=train_loader,
                                                                                       dataset_name=self.trainer.train_loader.dataset_name,
                                                                                       dataset_tag=self.trainer.train_loader.dataset_tag)

        self.evaluator.eval_component.dataset_loaders = {key: DatasetLoaderFactory.get_data_loader_shard_wrapper(
            data_loader_shard=self.accelerator.prepare(data_loader),
            dataset_name=data_loader.dataset_name,
            dataset_tag=data_loader.dataset_tag) for key, data_loader in self.evaluator.eval_component.dataset_loaders.items()}

        partial_batch_done_callback = partial(self.batch_processed_callback, experiment_status_logger=self._experiment_status_logger)
        def evaluation_step_routine(current_epoch: int): return self._evaluation_step(current_epoch=current_epoch)
        partial_train_epoch_done_callback = partial(self.train_epoch_done_callback, evaluation_step_routine=evaluation_step_routine, 
                                                    accelerator=self.accelerator)

        model = self.trainer.train(num_epochs=self.num_epochs, model=self.model, optimizer=self.optimizer,
                                   batch_done_callback_fun=partial_batch_done_callback,
                                   epoch_done_callback=partial_train_epoch_done_callback, accelerator=self.accelerator,
                                   num_batches_per_epoch=self.num_batches_per_epoch)
        self.accelerator.free_memory()

    def _execute_warm_start(self):
        """ 
        Execute warm start of the model from an epoch.
        """
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

        self._execute_train()
