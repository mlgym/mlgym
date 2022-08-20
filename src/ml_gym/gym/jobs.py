from abc import abstractmethod
from ml_gym.models.nn.net import NNModel
from ml_gym.gym.evaluator import Evaluator
from ml_gym.gym.trainer import Trainer
from ml_gym.modes import RunMode
from ml_gym.optimizers.optimizer import OptimizerAdapter
import torch
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.persistency.io import DashifyReader
from ml_gym.persistency.io import DashifyWriter
from typing import List, Dict, Any
from ml_gym.util.logger import ConsoleLogger, LogLevel
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.persistency.logging import ExperimentStatusLogger
from functools import partial


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
    def from_blue_print(blue_print) -> 'AbstractGymJob':
        return blue_print.construct()

    def save_state_of_stateful_components(self, measurement_id: int):
        # save model and optimizer
        # TODO PriyaTomar
        # we need to send checkpoint to the backend server
        # Strategy object requires evaluation_result and based on that we decide if we want to store or not
        # Strategy object is being passed from possibly outside of MLgym
        state = self.get_state()
        DashifyWriter.save_state(experiment_info=self.experiment_info, data_dict=state, measurement_id=measurement_id)

    def restore_state_in_stateful_components(self, measurement_id: int):
        state = DashifyReader.load_state(experiment_info=self.experiment_info, measurement_id=measurement_id)
        self.set_state(state)

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

    def __init__(self, run_mode: RunMode, model: NNModel, optimizer: OptimizerAdapter, trainer: Trainer,
                 evaluator: Evaluator, epochs: List[int], current_epoch: int = 0,
                 experiment_status_logger: ExperimentStatusLogger = None):
        super().__init__(experiment_status_logger)
        self.run_mode = run_mode
        self.model = model
        self.optimizer = optimizer
        self.optimizer.register_model_params(dict(self.model.named_parameters()))
        self.epochs = epochs
        self.current_epoch = current_epoch if current_epoch is not None else 0
        self.evaluator = evaluator
        self.trainer = trainer
        self._execution_method = self._execute_eval if run_mode == RunMode.RE_EVAL else self._execute_train

    def _train_step(self, device: torch.device, epoch: int) -> NNModel:
        # self.restore_state_in_stateful_components(epoch - 1)
        # load model and optimizer
        # model_state = DashifyReader.load_model_state(self._experiment_info, epoch - 1)
        # self.model.load_state_dict(model_state)
        # self.model.to(device)
        # optimizer_state = DashifyReader.load_optimizer_state(self._experiment_info, epoch - 1)
        # self.optimizer.load_state_dict(optimizer_state)
        # train
        partial_batch_processed_callback = partial(self.batch_processed_callback, num_epochs=self.epochs, current_epoch=epoch,
                                                   experiment_status_logger=self._experiment_status_logger)
        model = self.trainer.train_epoch(self.model, self.optimizer, device,
                                         batch_processed_callback_fun=partial_batch_processed_callback)
        return model

    def _evaluation_step(self, device: torch.device, epoch: int):
        self.model.to(device)
        partial_batch_processed_callback = partial(self.batch_processed_callback, num_epochs=self.epochs, current_epoch=epoch,
                                                   experiment_status_logger=self._experiment_status_logger)
        partial_epoch_result_callback = partial(self.epoch_result_callback, current_epoch=epoch,
                                                experiment_status_logger=self._experiment_status_logger)

        evaluation_result = self.evaluator.evaluate(model=self.model,
                                                    device=device,
                                                    current_epoch=epoch,
                                                    num_epochs=self.epochs,
                                                    batch_processed_callback_fun=partial_batch_processed_callback,
                                                    epoch_result_callback_fun=partial_epoch_result_callback)

        # save model and optimizer
        # TODO PriyaTomar
        # we need to send checkpoint to the backend server
        # Strategy object requires evaluation_result and based on that we decide if we want to store or not
        # Strategy object is being passed from possibly outside of MLgym

        # DashifyWriter.save_binary_state("model", self.model.state_dict(), self._experiment_info, epoch)
        # DashifyWriter.save_binary_state("optimizer", self.optimizer.state_dict(), self._experiment_info, epoch)
        # self.save_state_of_stateful_components(measurement_id=epoch)

        # DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=epoch)

    def execute(self, device: torch.device):
        """ Executes the job

        Args:
            device: torch device either CPUs or a specified GPU
        """
        self._execution_method(device)

    def _execute_train(self, device: torch.device):
        self.trainer.set_num_epochs(num_epochs=self.epochs)

        if self.run_mode == RunMode.TRAIN:
            # save model and optimizer
            # TODO PriyaTomar
            # we need to send checkpoint to the backend server
            # Strategy object requires evaluation_result and based on that we decide if we want to store or not
            # Strategy object is being passed from possibly outside of MLgym
            # DashifyWriter.save_binary_state("model", self.model.state_dict(), self._experiment_info, 0)
            # we only register the model parameters here, so we can instantiate the internal optimizer within
            # OptimizerAdapter. Only then, we can retrieve the state_dict of the internal optimizer.
            # self.optimizer.register_model_params(model_params=dict(self.model.named_parameters()))
            # DashifyWriter.save_binary_state("optimizer", self.optimizer.state_dict(), self._experiment_info, 0)
            # self.save_state_of_stateful_components(0)
            pass
        elif self.run_mode == RunMode.WARM_START:
            self.optimizer.register_model_params(model_params=dict(self.model.named_parameters()))

        self._evaluation_step(device, epoch=self.current_epoch)
        self.current_epoch += 1
        self.trainer.set_current_epoch(self.current_epoch)
        while not self.trainer.is_done():
            self.logger.log(LogLevel.INFO,  f"epoch: {self.current_epoch}")
            self._train_step(device, epoch=self.current_epoch)
            self._evaluation_step(device, epoch=self.current_epoch)
            self.current_epoch += 1

    def _execute_eval(self, device: torch.device):
        for epoch in self.epochs:
            self._evaluation_step(device, measurement_id=epoch)


class GymJobFactory:
    @staticmethod
    def get_gym_job(run_mode: RunMode, epochs: List[int], experiment_status_logger: ExperimentStatusLogger = None,
                    **components: Dict[str, Any]) -> AbstractGymJob:
        return GymJob(run_mode=run_mode, epochs=epochs, experiment_status_logger=experiment_status_logger, **components)
