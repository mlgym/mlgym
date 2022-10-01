from abc import abstractmethod
from ml_gym.early_stopping.early_stopping_strategies import EarlyStoppingIF
from ml_gym.models.nn.net import NNModel
from ml_gym.gym.evaluator import Evaluator
from ml_gym.gym.trainer import Trainer
from ml_gym.modes import RunMode
from ml_gym.optimizers.optimizer import OptimizerAdapter
import torch
from ml_gym.gym.stateful_components import StatefulComponent
from typing import List, Dict, Any
from ml_gym.util.logger import ConsoleLogger, LogLevel
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.persistency.logging import ExperimentStatusLogger
from functools import partial
from ml_gym.persistency.io import GridSearchAPIClientIF, CheckpointResource
import pickle
from ml_gym.checkpointing.checkpointing import CheckpointingIF, CheckpointingInstruction


class AbstractGymJob(StatefulComponent):

    def __init__(self, experiment_status_logger: ExperimentStatusLogger):
        super().__init__()
        self._experiment_status_logger = experiment_status_logger
        # TODO: This is only a console logger that does not store on disk.
        # Since GymJob is a StatefulComponent we would have to implement serialization
        # for the queue in the QLogger. Solving this issue is left for the future
        self.logger = ConsoleLogger("logger_gym_job")

    @abstractmethod
    def execute(self, device: torch.device):
        raise NotImplementedError

    @staticmethod
    def from_blue_print(blue_print, device: torch.device) -> 'AbstractGymJob':
        return blue_print.construct(device)

    # def restore_state_in_stateful_components(self, measurement_id: int):
    #     state = DashifyReader.load_state(experiment_info=self.experiment_info, measurement_id=measurement_id)
    #     self.set_state(state)

    @staticmethod
    def batch_processed_callback(status: str, experiment_status_logger: ExperimentStatusLogger, num_batches: int,
                                 current_batch: int, splits: List[str], current_split: str, num_epochs: int, current_epoch: int):
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


class GymJob(AbstractGymJob):

    def __init__(self, grid_search_id: str, experiment_id: int,  run_mode: RunMode, model: NNModel, optimizer: OptimizerAdapter,
                 trainer: Trainer, evaluator: Evaluator, num_epochs: int, checkpointing_strategy: CheckpointingIF,
                 gs_api_client: GridSearchAPIClientIF, experiment_status_logger: ExperimentStatusLogger = None,
                 early_stopping_strategy: EarlyStoppingIF = None, warm_start_epoch: int = 0):
        super().__init__(experiment_status_logger)
        self.grid_search_id = grid_search_id
        self.experiment_id = experiment_id
        self.run_mode = run_mode
        self.model = model
        self.optimizer = optimizer
        # self.optimizer.register_model_params(dict(self.model.named_parameters()))
        self.num_epochs = num_epochs
        self.current_epoch = warm_start_epoch
        self.evaluator = evaluator
        self.trainer = trainer
        self.checkpointing_strategy = checkpointing_strategy
        self.early_stopping_strategy = early_stopping_strategy
        self.gs_api_client = gs_api_client
        if run_mode == RunMode.TRAIN:
            self._execution_method = self._execute_train
        elif run_mode == RunMode.WARM_START:
            self._execution_method = self._execute_warm_start
        else:
            raise NotImplementedError

    def _train_step(self, device: torch.device) -> NNModel:
        # self.restore_state_in_stateful_components(epoch - 1)
        # load model and optimizer
        # model_state = DashifyReader.load_model_state(self._experiment_info, epoch - 1)
        # self.model.load_state_dict(model_state)
        # self.model.to(device)
        # optimizer_state = DashifyReader.load_optimizer_state(self._experiment_info, epoch - 1)
        # self.optimizer.load_state_dict(optimizer_state)
        # train
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
        if checkpoint_instruction.save_current:
            self._experiment_status_logger.log_checkpoint(self.current_epoch, self.model.state_dict(), self.optimizer.state_dict(),
                                                          self.get_state())
        for epoch in checkpoint_instruction.checkpoints_to_delete:
            self._experiment_status_logger.log_checkpoint(epoch=epoch, model_binary_stream=None,
                                                          optimizer_binary_stream=None, stateful_components_binary_stream=None)

    def execute(self, device: torch.device):
        """ Executes the job

        Args:
            device: torch device either CPUs or a specified GPU
        """
        self._execution_method(device)

    def _execute_train(self, device: torch.device):
        self.optimizer.register_model_params(model_params=dict(self.model.named_parameters()))

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

        # start the actual training loop
        self.current_epoch += 1
        self.trainer.set_current_epoch(self.current_epoch)
        while not self.trainer.is_done():
            self.logger.log(LogLevel.INFO,  f"epoch: {self.current_epoch}")
            self._train_step(device)
            evaluation_results = self._evaluation_step(device)
            checkpointing_instruction = self.checkpointing_strategy.get_model_checkpoint_instruction(num_epochs=self.num_epochs,
                                                                                                     current_epoch=self.current_epoch,
                                                                                                     evaluation_result=evaluation_results)
            self.run_checkpointing(checkpointing_instruction)
            if self.early_stopping_strategy.is_stopping_criterion_fulfilled(current_epoch=self.current_epoch,
                                                                            evaluation_results=evaluation_results):
                break

            self.current_epoch += 1

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

            state_component_state = pickle.loads(self.gs_api_client.get_checkpoint_resource(grid_search_id=self.grid_search_id,
                                                                                            experiment_id=self.experiment_id,
                                                                                            checkpoint_id=self.current_epoch,
                                                                                            checkpoint_resource=CheckpointResource.stateful_components))
            self.set_state(state_component_state)

        self._execute_train(device)

    def _execute_eval(self, device: torch.device):
        for epoch in self.num_epochs:
            # TODO need to load model + stateful components for the respective epoch here
            self._evaluation_step(device, epoch=epoch)


class GymJobFactory:
    @staticmethod
    def get_gym_job(grid_search_id: str, experiment_id: int, run_mode: RunMode, num_epochs: int, gs_api_client: GridSearchAPIClientIF,
                    experiment_status_logger: ExperimentStatusLogger = None, warm_start_epoch: int = 0,
                    **components: Dict[str, Any]) -> AbstractGymJob:
        return GymJob(grid_search_id=grid_search_id, experiment_id=experiment_id, run_mode=run_mode, num_epochs=num_epochs,
                      gs_api_client=gs_api_client, experiment_status_logger=experiment_status_logger,
                      warm_start_epoch=warm_start_epoch, **components)
