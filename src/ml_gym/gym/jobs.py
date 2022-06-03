from ml_gym.persistency.state_logging import StateLoggingIF
from ml_gym.util.logger import ConsoleLogger
from typing import List, Dict, Any
from enum import Enum
from ml_gym.persistency.io import DashifyWriter
from ml_gym.persistency.io import DashifyReader
from ml_gym.gym.stateful_components import StatefulComponent
import torch
from ml_gym.optimizers.optimizer import OptimizerAdapter
from ml_gym.modes import RunMode
from abc import ABC, abstractmethod, abstractstaticmethod
from ml_gym.batching.batch import EvaluationBatchResult
from ml_gym.models.nn.net import NNModel
from dashify.logging.dashify_logging import ExperimentInfo
from ml_gym.gym.evaluator import Evaluator
from ml_gym.gym.trainer import Trainer
<< << << < HEAD
== == == =
>>>>>> > warm_start


class AbstractGymJob(StatefulComponent):

    class Type(Enum):
        STANDARD = "standard"

    def __init__(self, experiment_info: ExperimentInfo):
        super().__init__()
        self._experiment_info = experiment_info
        # TODO: This is only a console logger that does not store on disk.
        # Since GymJob is a StatefulComponent we would have to implement serialization
        # for the queue in the QLogger. Solving this issue is left for the future
        self.logger = ConsoleLogger("logger_gym_job")

    @property
    def experiment_info(self) -> ExperimentInfo:
        return self._experiment_info

    @abstractmethod
    def execute(self, device: torch.device):
        raise NotImplementedError

    @staticmethod
    def from_blue_print(blue_print) -> 'AbstractGymJob':
        return blue_print.construct()

    # def save_state_of_stateful_components(self, measurement_id: int):
    #     state = self.get_state()
    #     DashifyWriter.save_state(experiment_info=self.experiment_info, data_dict=state, measurement_id=measurement_id)

    # def restore_state_in_stateful_components(self, measurement_id: int):
    #     state = DashifyReader.load_state(experiment_info=self.experiment_info, measurement_id=measurement_id)
    #     self.set_state(state)


class GymJob(AbstractGymJob):

    def __init__(self, run_mode: AbstractGymJob.Mode.TRAIN, model: NNModel, trainer: Trainer,
                 evaluator: Evaluator, experiment_info: ExperimentInfo, epochs: List[int],
                 state_logging: StateLoggingIF):
        super().__init__(experiment_info)
        self.run_mode = run_mode
        self.model = model
        self.epochs = epochs
        self.evaluator = evaluator
        self.trainer = trainer
        self._execution_method = self._execute_eval if run_mode == RunMode.RE_EVAL else self._execute_train
        self.state_logging = state_logging

    def _train_step(self, device: torch.device, epoch: int) -> NNModel:
        # self.restore_state_in_stateful_components(epoch - 1)
        # load model and trainer state
        # model_state = DashifyReader.load_model_state(self._experiment_info, epoch - 1)
        # self.model.load_state_dict(model_state)
        self.model.to(device)
        # trainer_state = DashifyReader.load_trainer_state(self._experiment_info, epoch - 1)
        # self.trainer.set_state(trainer_state)
        model = self.trainer.train_epoch(self.model, device)
        return model

    def _evaluation_step(self, device: torch.device, epoch: int):
        # self.restore_state_in_stateful_components(epoch)
        # model_state = DashifyReader.load_model_state(self._experiment_info, epoch)
        # self.model.load_state_dict(model_state)
        self.model.to(device)
        evaluation_result = self.evaluator.evaluate(self.model, device)
        return evaluation_result

    def execute(self, device: torch.device):
        """ Executes the job

        Args:
            device: torch device either CPUs or a specified GPU
        """
        self._execution_method(device)

    def _execute_train(self, device: torch.device):
        trained_epochs = max(DashifyReader.get_last_epoch(self.experiment_info), 0)
        if trained_epochs == 0:
            evaluation_result = self._evaluation_step(device, trained_epochs)
            DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=trained_epochs)
            self.state_logging.log_state(key="model", state_dict=self.model.state_dict(), eval_results=evaluation_result,
                                         experiment_info=self._experiment_info, epoch=trained_epochs)

        if trained_epochs > 0:
            model_state = self.state_logging.load_state(key="model", experiment_info=self._experiment_info, epoch=trained_epochs)
            self.model.load_state_dict(model_state)
            trainer_state = self.state_logging.load_state(key="trainer", experiment_info=self._experiment_info, epoch=trained_epochs)
            self.trainer.set_state(trainer_state)

        self.trainer.set_num_epochs(num_epochs=self.epochs)
        self.trainer.set_current_epoch(trained_epochs+1)
        while not self.trainer.is_done():
            current_epoch = self.trainer.current_epoch
            # train epoch
            self._train_step(device, epoch=current_epoch)
            # eval epoch
            evaluation_result = self._evaluation_step(device, current_epoch)
            # save artifacts
            self.state_logging.log_state(key="model", state_dict=self.model.state_dict(), eval_results=evaluation_result,
                                         experiment_info=self._experiment_info, epoch=current_epoch)
            self.state_logging.log_state(key="trainer", state_dict=self.trainer.get_state(), eval_results=evaluation_result,
                                         experiment_info=self._experiment_info, epoch=current_epoch)
            # save results
            DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=current_epoch)

    def _execute_eval(self, device: torch.device):
        for epoch in self.epochs:
            evaluation_result = self._evaluation_step(device, measurement_id=epoch)
            DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=epoch)


# class GymJobLite(AbstractGymJob):

#     def __init__(self, run_mode: AbstractGymJob.Mode, model: NNModel, trainer: Trainer,
#                  evaluator: Evaluator, experiment_info: ExperimentInfo, epochs: List[int]):
#         super().__init__(experiment_info)
#         self.run_mode = run_mode
#         self.model = model
#         self.optimizer.register_model_params(dict(self.model.named_parameters()))
#         self.epochs = epochs
#         self.evaluator = evaluator
#         self.trainer = trainer
#         self._execution_method = self._execute_train if run_mode == GymJob.Mode.TRAIN else self._execute_eval

#     def _train_step(self, device: torch.device, epoch: int) -> NNModel:
#         # self.restore_state_in_stateful_components(measurement_id - 1)
#         # load model and optimizer
#         # model_state = DashifyReader.load_model_state(self._experiment_info, measurement_id - 1)
#         self.model.to(device)
#         # train
#         self.model = self.trainer.train_epoch(self.model, self.optimizer, device)
#         return self.model

#     def _evaluation_step(self, device: torch.device, measurement_id: int):
#         self.model.to(device)
#         evaluation_result = self.evaluator.evaluate(self.model, device)
#         DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=measurement_id)

#     def execute(self, device: torch.device):
#         """ Executes the job

#         Args:
#             device: torch device either CPUs or a specified GPU
#         """
#         self._execution_method(device)

#     def _execute_train(self, device: torch.device):
#         trained_epochs = max(DashifyReader.get_last_epoch(self.experiment_info), 0)
#         self.trainer.set_num_epochs(num_epochs=self.epochs)
#         self.trainer.set_current_epoch(trained_epochs+1)
#         while not self.trainer.is_done():
#             current_epoch = self.trainer.current_epoch
#             # self.logger.log(LogLevel.DEBUG, "Executing evaluation step")
#             self._evaluation_step(device, current_epoch-1)
#             # self.logger.log(LogLevel.DEBUG, "Executing training step")
#             model = self._train_step(device, epoch=current_epoch)
#         self._evaluation_step(device, current_epoch)

#         # log the final model / training state
#         DashifyWriter.save_binary_state("model", model.state_dict(), self._experiment_info, current_epoch)
#         DashifyWriter.save_binary_state("optimizer", self.optimizer.state_dict(), self._experiment_info, current_epoch)
#         self.save_state_of_stateful_components(measurement_id=current_epoch)

#     def _execute_eval(self, device: torch.device):
#         for epoch in self.epochs:
#             self._evaluation_step(device, measurement_id=epoch)


class GymJobFactory:
    @staticmethod
    def get_gym_job(run_mode: RunMode, experiment_info: ExperimentInfo, epochs: List[int],
                    job_type: AbstractGymJob.Type = AbstractGymJob.Type.STANDARD, **components: Dict[str, Any]) -> AbstractGymJob:
        if job_type == AbstractGymJob.Type.STANDARD:
            return GymJob(run_mode=run_mode, experiment_info=experiment_info, epochs=epochs, **components)
        else:
            raise NotImplementedError(f"job type {job_type} is not implemented")
