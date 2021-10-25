from abc import ABC, abstractmethod
from ml_gym.gym.evaluator import EvaluationBatchResult
from typing import List, Dict, Any, BinaryIO
from dashify.logging.dashify_logging import ExperimentInfo, DashifyLogger
import glob
import os
from ml_gym.error_handling.exception import TrainingStateCorruptError
import json


class AbstractWriter(ABC):
    @staticmethod
    @abstractmethod
    def log_console(result: EvaluationBatchResult):
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def log_measurement_result(results: List[EvaluationBatchResult], experiment_info: ExperimentInfo,
                               measurement_id: int):
        raise NotImplementedError


class DashifyWriter(AbstractWriter):
    """ Partially wraps the `DashifyLogger`.
    """

    @staticmethod
    def log_console(result: EvaluationBatchResult):
        result.aggregate()
        print(str(result))

    @staticmethod
    def save_state(data_dict: Dict[str, Any], experiment_info: ExperimentInfo, measurement_id: int = 0):
        file_name = f"state_{str(measurement_id)}.json"
        DashifyLogger.save_dict(file_name, data_dict, experiment_info)

    @staticmethod
    def log_measurement_result(results: List[EvaluationBatchResult], experiment_info: ExperimentInfo,
                               measurement_id: int):
        results_dict = {}
        for result in results:
            metrics_dictionary = DashifyWriter._get_results_dict(result)
            results_dict = {**metrics_dictionary, **results_dict}
        DashifyLogger.log_metrics(experiment_info=experiment_info, metrics=results_dict, measurement_id=measurement_id)

    @staticmethod
    def save_binary_state(key: str, state: BinaryIO, experiment_info: ExperimentInfo, measurement_id: int):
        DashifyLogger.save_checkpoint_state_dict(state, key, experiment_info, measurement_id)

    # @staticmethod
    # def save_model_state(model_state: Dict, experiment_info: ExperimentInfo, measurement_id: int):
    #     DashifyLogger.save_checkpoint_state_dict(model_state, "model", experiment_info, measurement_id)

    # @staticmethod
    # def save_optimizer_state(optimizer_state: Dict, experiment_info: ExperimentInfo, measurement_id: int):
    #     DashifyLogger.save_checkpoint_state_dict(optimizer_state, "optimizer", experiment_info, measurement_id)

    @staticmethod
    def _get_results_dict(result: EvaluationBatchResult) -> Dict[str, List[float]]:
        def combine_metric_name(dataset_split: str, metric_name: str):
            return f"{dataset_split}/{metric_name.lower()}"

        # get metrics and losses as dict
        results_dict = dict()
        metrics_and_losses = {**result.metrics, **result.losses}
        for metric_name, metric_value in metrics_and_losses.items():
            results_dict[combine_metric_name(result.split_name, metric_name)] = metric_value
        return results_dict


class DashifyReader:

    @staticmethod
    def load_model_state(experiment_info: ExperimentInfo, measurement_id: int) -> Dict:
        model_state = DashifyLogger.load_checkpoint_state_dict("model", experiment_info, measurement_id)
        return model_state

    @staticmethod
    def experiments_exist(experiment_info: ExperimentInfo, measurement_id: int) -> bool:
        try:
            DashifyReader.load_model_state(experiment_info, measurement_id)
        except:
            return False
        return True

    @staticmethod
    def load_optimizer_state(experiment_info: ExperimentInfo, measurement_id: int) -> Dict:
        optimizer_state = DashifyLogger.load_checkpoint_state_dict("optimizer", experiment_info, measurement_id)
        return optimizer_state

    @staticmethod
    def load_state(experiment_info: ExperimentInfo, measurement_id: int = 0) -> Dict[str, Any]:
        file_name = f"state_{str(measurement_id)}.json"
        data_dict = DashifyLogger.load_dict(file_name, experiment_info)
        return data_dict

    @staticmethod
    def get_last_epoch(experiment_info: ExperimentInfo) -> int:
        # TODO integrate into DashifyML
        # get epoch of latest model
        checkpoint_folder_path = os.path.join(experiment_info.full_experiment_path, DashifyLogger.checkpoint_folder)
        model_paths = glob.glob(os.path.join(checkpoint_folder_path, "model_*.pt"))
        if not model_paths:
            model_epoch = -1
        else:
            model_epoch = max([int(p.split("model_")[-1][:-3]) for p in model_paths])

        # get epoch according to metrics
        metrics_path = os.path.join(experiment_info.full_experiment_path, "metrics.json")
        with open(metrics_path, "r") as f:
            metrics = json.load(f)
        if not metrics.keys():
            metric_epoch = -1
        else:
            metric_epoch = len(metrics[list(metrics.keys())[0]]) - 1

        # final check
        if model_epoch != metric_epoch:
            raise TrainingStateCorruptError(
                f"The experiment {experiment_info.experiment_id} has checkpointed the model at epoch {model_epoch} and but has evaluated the model until epoch {metric_epoch}.")
        return model_epoch
