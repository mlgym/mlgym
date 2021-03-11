from abc import abstractmethod
import glob
import os
from abc import ABC
from typing import Callable, Dict, List, Any
import json
import tqdm
from collections import defaultdict
import numpy as np


class EvaluationAnalyzerIF(ABC):

    @abstractmethod
    def analyze(self):
        raise NotImplementedError


class ExperimentRatingStrategyIf(ABC):

    @abstractmethod
    def __call__(self) -> float:
        raise NotImplementedError


class ExperimentRepresentation:
    def __init__(self, config_path: str, metric_path: str):
        self.config_path = config_path
        self.metric_path = metric_path
        with open(config_path, "r") as f:
            self.config = json.load(f)
        with open(metric_path, "r") as f:
            self.results = json.load(f)
            self.results = {key: np.array(result_list) for key, result_list in self.results.items()}

        self.experiment_id = self.config["nested_cv_experiment_information"]["config"]["experiment_id"]
        self.hyper_paramater_combination_id = self.config["nested_cv_experiment_information"]["config"]["hyper_paramater_combination_id"]
        self.outer_test_fold_id = self.config["nested_cv_experiment_information"]["config"]["outer_test_fold_id"]
        self.inner_test_fold_id = self.config["nested_cv_experiment_information"]["config"]["inner_test_fold_id"]


class NestedCVRepresentation:
    def __init__(self) -> None:
        # outer fold id -> hpc_id -> Experiment
        self.outer_experiments: Dict[int, Dict[int, ExperimentRepresentation]] = {}
        # outer fold id -> inner fold id -> hpc_id -> Experiment
        self.inner_experiments: Dict[int, Dict[int, Dict[int, ExperimentRepresentation]]] = {}

    def add_experiment(self, e: ExperimentRepresentation):
        # outer folds
        if e.inner_test_fold_id == -1:
            if e.outer_test_fold_id not in self.outer_experiments:
                self.outer_experiments[e.outer_test_fold_id] = {}
            self.outer_experiments[e.outer_test_fold_id][e.hyper_paramater_combination_id] = e
        # inner folds
        if e.inner_test_fold_id > -1:
            if e.outer_test_fold_id not in self.inner_experiments:
                self.inner_experiments[e.outer_test_fold_id] = {}
            if e.inner_test_fold_id not in self.inner_experiments[e.outer_test_fold_id]:
                self.inner_experiments[e.outer_test_fold_id][e.inner_test_fold_id] = {}
            self.inner_experiments[e.outer_test_fold_id][e.inner_test_fold_id][e.hyper_paramater_combination_id] = e

    def get_hyper_parameter_combination_ids(self) -> List[int]:
        return list(self.outer_experiments[0].keys())

    def verify(self) -> bool:
        experiment_ids = set(self.outer_experiments[0].keys())
        for _, fold in self.outer_experiments.items():
            if set(fold.keys()) != experiment_ids:
                return False

        for _, outer_fold in self.inner_experiments.items():
            for _, inner_fold in outer_fold.items():
                if set(inner_fold.keys()) != experiment_ids:
                    return False
        return True


class NestedCVReport:
    def __init__(self, nested_cv_path: str, experiments: List[ExperimentRepresentation], epoch: int):
        self.nested_cv_path = nested_cv_path
        self.experiments = experiments
        self.report = self.calc_report(self.experiments)
        self.epoch = epoch

    @staticmethod
    def calc_report(experiments: List[ExperimentRepresentation]) -> Dict[str, Any]:
        results_list: List[Dict[str, Any]] = [e.results for e in experiments]
        aggregated_metrics = {"avg_scores": {}, "std": {}}
        for metric_key in results_list[0].keys():
            aggregated_metrics["avg_scores"][metric_key] = np.mean(np.array([result[metric_key] for result in results_list]), axis=0)
            aggregated_metrics["std"][metric_key] = np.std(np.array([result[metric_key] for result in results_list]), axis=0)

        return aggregated_metrics

    def __repr__(self):
        avg_scores = self.report["avg_scores"]
        stds = self.report["std"]
        metris_string = [f'{metric_key + ":":50} {metric_scores[self.epoch]:10.4f} ({stds[metric_key][self.epoch]:.4f})'
                         for metric_key, metric_scores in avg_scores.items() if len(metric_scores.shape) == 1]

        report = \
            f"NESTED CV REPORT: {self.nested_cv_path} \n" + \
            f"Experiment ids: {[e.experiment_id for e in self.experiments]} \n" + \
            f"Hyper parameter combination ids: {[e.hyper_paramater_combination_id for e in self.experiments]} \n" + \
            "METRICS: \n" + \
            "\n".join(metris_string)
        return report


class NestedCVAnalyzer(EvaluationAnalyzerIF):
    def __init__(self, result_directory: str, scoring_fun: Callable[[ExperimentRepresentation], float]):
        self.result_directory = result_directory
        self.scoring_fun = scoring_fun

    @staticmethod
    def _load_experiments(result_directory: str) -> NestedCVRepresentation:
        nested_cv_representation = NestedCVRepresentation()
        metric_paths = list(sorted(glob.glob(os.path.join(result_directory, "**/*metrics.json"), recursive=True)))
        config_paths = list(sorted(glob.glob(os.path.join(result_directory, "**/*config.json"), recursive=True)))
        experiment_representations = [ExperimentRepresentation(config_path=config_path, metric_path=metric_path)
                                      for metric_path, config_path in tqdm.tqdm(zip(metric_paths, config_paths), desc="Loading experiments")]
        for e in experiment_representations:
            nested_cv_representation.add_experiment(e)
        return nested_cv_representation

    @staticmethod
    def _select_best_model_of_inner_fold(outer_fold_id: int, nested_cv_representation: NestedCVRepresentation,
                                         scoring_fun: Callable[[ExperimentRepresentation], float]) -> int:
        # inner fold id -> hpc_id -> Experiment
        experiments = nested_cv_representation.inner_experiments[outer_fold_id]
        # hpc_id -> [score_1, score_2]
        scores = defaultdict(list)
        for _, inner_fold in experiments.items():
            for hpc_id, experiment in inner_fold.items():
                scores[hpc_id].append(scoring_fun(experiment=experiment))

        # average the scores for hcp_id combination over the inner folds
        avg_scores = {key: np.mean(score) for key, score in scores.items()}
        keys = list(avg_scores.keys())
        values = list(avg_scores.values())
        best_hpc_id = keys[np.argmax(values)]
        return best_hpc_id

    def analyze(self, epoch: int) -> NestedCVReport:
        nested_cv_representation = self._load_experiments(self.result_directory)
        if not nested_cv_representation.verify():
            raise Exception("Corrputed Nested CV representation!")
        # we aggregate the scores on the inner folds and select the experiment in the outer fold
        # whose hyper parameter combinations had the best score on the inner folds
        best_full_experiments: List[ExperimentRepresentation] = []
        for outer_fold_id in nested_cv_representation.inner_experiments.keys():
            bets_hpc_id = self._select_best_model_of_inner_fold(outer_fold_id=outer_fold_id,
                                                                nested_cv_representation=nested_cv_representation,
                                                                scoring_fun=self.scoring_fun)
            best_experiment = nested_cv_representation.outer_experiments[outer_fold_id][bets_hpc_id]
            best_full_experiments.append(best_experiment)
        report = NestedCVReport(self.result_directory, best_full_experiments, epoch)
        return report


def scoring_fun_single_scalar_metric(metric_key: str, experiment: ExperimentRepresentation, epoch: int = -1) -> float:
    return experiment.results[metric_key][epoch]


# if __name__ == "__main__":
#     from functools import partial

#     epoch = -1
#     scoring_fun = partial(scoring_fun_single_scalar_metric, metric_key="train/auroc_macro", epoch=epoch)

#     result_directory = ""
#     analyzer = NestedCVAnalyzer(result_directory, scoring_fun=scoring_fun)
#     report = analyzer.analyze(epoch)
#     print(report)
