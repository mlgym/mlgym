from abc import abstractmethod
from ml_gym.models.nn.net import NNModel
from dashify.logging.dashify_logging import ExperimentInfo
from ml_gym.gym.evaluator import Evaluator
from ml_gym.gym.trainer import Trainer
from ml_gym.optimizers.optimizer import OptimizerAdapter
import torch
from ml_gym.gym.stateful_components import StatefulComponent
from ml_gym.persistency.io import DashifyReader
from ml_gym.persistency.io import DashifyWriter
from enum import Enum
from typing import List, Dict, Any
from ml_gym.util.logger import ConsoleLogger


class AbstractGymJob(StatefulComponent):
    class Mode(Enum):
        EVAL = "eval"
        TRAIN = "training"

    class Type(Enum):
        STANDARD = "standard"
        LITE = "lite"

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

    def save_state_of_stateful_components(self, measurement_id: int):
        state = self.get_state()
        DashifyWriter.save_state(experiment_info=self.experiment_info, data_dict=state, measurement_id=measurement_id)

    def restore_state_in_stateful_components(self, measurement_id: int):
        state = DashifyReader.load_state(experiment_info=self.experiment_info, measurement_id=measurement_id)
        self.set_state(state)


class GymJob(AbstractGymJob):

    def __init__(self, run_mode: AbstractGymJob.Mode.TRAIN, model: NNModel, optimizer: OptimizerAdapter, trainer: Trainer,
                 evaluator: Evaluator, experiment_info: ExperimentInfo, epochs: List[int]):
        super().__init__(experiment_info)
        self.run_mode = run_mode
        self.model = model
        self.optimizer = optimizer
        self.epochs = epochs
        self.evaluator = evaluator
        self.trainer = trainer
        if self.run_mode == AbstractGymJob.Mode.TRAIN and epochs[0] == 0:
            # save model state
            DashifyWriter.save_binary_state("model", model.state_dict(), self._experiment_info, 0)
            self.optimizer.register_model_params(params=self.model.parameters())
            DashifyWriter.save_binary_state("optimizer", optimizer.state_dict(), self._experiment_info, 0)
        self._execution_method = self._execute_train if run_mode == GymJob.Mode.TRAIN else self._execute_eval

    def _train_step(self, device: torch.device, measurement_id: int) -> NNModel:
        self.restore_state_in_stateful_components(measurement_id - 1)
        # load model and optimizer
        model_state = DashifyReader.load_model_state(self._experiment_info, measurement_id - 1)
        self.model.load_state_dict(model_state)
        self.model.to(device)
        self.optimizer.register_model_params(params=self.model.parameters())
        optimizer_state = DashifyReader.load_optimizer_state(self._experiment_info, measurement_id - 1)
        self.optimizer.load_state_dict(optimizer_state)
        # train
        model = self.trainer.train_epoch(self.model, self.optimizer, device)
        # save model and optimizer
        DashifyWriter.save_binary_state("model", model.state_dict(), self._experiment_info, measurement_id)
        DashifyWriter.save_binary_state("optimizer", self.optimizer.state_dict(), self._experiment_info, measurement_id)
        self.save_state_of_stateful_components(measurement_id=measurement_id)
        return model

    def _evaluation_step(self, device: torch.device, measurement_id: int):
        self.restore_state_in_stateful_components(measurement_id)
        model_state = DashifyReader.load_model_state(self._experiment_info, measurement_id)
        self.model.load_state_dict(model_state)
        self.model.to(device)
        evaluation_result = self.evaluator.evaluate(self.model, device)
        DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=measurement_id)

    def _warmup(self, device: torch.device, measurement_id: int):
        # self.evaluator.warm_up(self.model, device)
        # self.trainer.warm_up(self.model, device)
        self.save_state_of_stateful_components(measurement_id=measurement_id)

    def execute(self, device: torch.device):
        """ Executes the job

        Args:
            device: torch device either CPUs or a specified GPU
        """
        self._execution_method(device)

    def _execute_train(self, device: torch.device):
        step_epochs = self.epochs[1:]
        if len(self.epochs) > 0 and self.epochs[0] == 0:
            # perform warmup for trainer and evaluator components
            # self.logger.log(LogLevel.DEBUG, "Executing warmup step")
            self._warmup(device, measurement_id=0)
            # get initial results
            # self.logger.log(LogLevel.DEBUG, "Executing initial evaluation step")
            self._evaluation_step(device, measurement_id=0)
            # train and evaluate

        for epoch in step_epochs:
            # self.logger.log(LogLevel.DEBUG, "Executing training step")
            self._train_step(device, measurement_id=epoch)
            # self.logger.log(LogLevel.DEBUG, "Executing evaluation step")
            self._evaluation_step(device, epoch)

    def _execute_eval(self, device: torch.device):
        for epoch in self.epochs:
            self._evaluation_step(device, measurement_id=epoch)


class GymJobLite(AbstractGymJob):

    def __init__(self, run_mode: AbstractGymJob.Mode, model: NNModel, optimizer: OptimizerAdapter, trainer: Trainer,
                 evaluator: Evaluator, experiment_info: ExperimentInfo, epochs: List[int]):
        super().__init__(experiment_info)
        self.run_mode = run_mode
        self.model = model
        self.optimizer = optimizer
        self.epochs = epochs
        self.evaluator = evaluator
        self.trainer = trainer
        self.optimizer.register_model_params(params=self.model.parameters())  # TODO this is a little bit ugly.
        self._execution_method = self._execute_train if run_mode == GymJob.Mode.TRAIN else self._execute_eval

    def _train_step(self, device: torch.device, measurement_id: int) -> NNModel:
        # self.restore_state_in_stateful_components(measurement_id - 1)
        # load model and optimizer
        # model_state = DashifyReader.load_model_state(self._experiment_info, measurement_id - 1)
        self.model.to(device)
        # train
        self.model = self.trainer.train_epoch(self.model, self.optimizer, device)
        return self.model

    def _evaluation_step(self, device: torch.device, measurement_id: int):
        self.model.to(device)
        evaluation_result = self.evaluator.evaluate(self.model, device)
        DashifyWriter.log_measurement_result(evaluation_result, self._experiment_info, measurement_id=measurement_id)

    def execute(self, device: torch.device):
        """ Executes the job

        Args:
            device: torch device either CPUs or a specified GPU
        """
        self._execution_method(device)

    def _execute_train(self, device: torch.device):
        step_epochs = self.epochs[1:]
        if len(self.epochs) > 0 and self.epochs[0] == 0:
            # get initial results
            # self.logger.log(LogLevel.DEBUG, "Executing initial evaluation step")
            self._evaluation_step(device, measurement_id=0)
            # train and evaluate

        for epoch in step_epochs:
            # self.logger.log(LogLevel.DEBUG, "Executing training step")
            model = self._train_step(device, measurement_id=epoch)
            # self.logger.log(LogLevel.DEBUG, "Executing evaluation step")
            self._evaluation_step(device, epoch)

        # log the final model / training state
        DashifyWriter.save_binary_state("model", model.state_dict(), self._experiment_info, step_epochs[-1])
        DashifyWriter.save_binary_state("optimizer", self.optimizer.state_dict(), self._experiment_info, step_epochs[-1])
        self.save_state_of_stateful_components(measurement_id=step_epochs[-1])

    def _execute_eval(self, device: torch.device):
        for epoch in self.epochs:
            self._evaluation_step(device, measurement_id=epoch)


class GymJobFactory:
    @staticmethod
    def get_gym_job(run_mode: AbstractGymJob.Mode, experiment_info: ExperimentInfo, epochs: List[int],
                    job_type: AbstractGymJob.Type = AbstractGymJob.Type.STANDARD, **components: Dict[str, Any]) -> AbstractGymJob:
        if job_type == AbstractGymJob.Type.LITE:
            return GymJobLite(run_mode=run_mode, experiment_info=experiment_info, epochs=epochs, **components)
        else:
            return GymJob(run_mode=run_mode, experiment_info=experiment_info, epochs=epochs, **components)
