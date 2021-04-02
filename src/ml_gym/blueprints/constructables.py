from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union, Type
from dashify.logging.dashify_logging import DashifyLogger
from data_stack.dataset.iterator import DatasetIteratorIF
from data_stack.repository.repository import DatasetRepository
from abc import abstractmethod, ABC
from data_stack.io.storage_connectors import StorageConnectorFactory
from data_stack.mnist.factory import MNISTFactory
from ml_gym.data_handling.dataset_loader import DatasetLoader, DatasetLoaderFactory
from ml_gym.optimizers.optimizer_factory import OptimizerFactory
from ml_gym.models.nn.net import NNModel
from collections.abc import Mapping
from ml_gym.registries.class_registry import ClassRegistry
from ml_gym.gym.trainer import Trainer, TrainComponent, InferenceComponent
from ml_gym.loss_functions.loss_functions import Loss
from sklearn.metrics import f1_score, recall_score, precision_score
from ml_gym.metrics.metrics import Metric, binary_aupr_score, binary_auroc_score
from ml_gym.metrics.metric_factory import MetricFactory
from ml_gym.gym.evaluator import Evaluator, EvalComponent
from ml_gym.data_handling.postprocessors.factory import ModelGymInformedIteratorFactory
from ml_gym.data_handling.postprocessors.collator import CollatorIF
from ml_gym.gym.post_processing import PredictPostProcessingIF, SoftmaxPostProcessorImpl, \
    ArgmaxPostProcessorImpl, SigmoidalPostProcessorImpl, DummyPostProcessorImpl, PredictPostProcessing, \
    BinarizationPostProcessorImpl
from data_stack.dataset.meta import MetaFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from functools import partial
from ml_gym.loss_functions.loss_factory import LossFactory


@dataclass
class Requirement:
    components: Union[Dict, List, Any] = None
    subscription: List[Union[str, int]] = field(default_factory=list)

    def get_subscription(self) -> Union[Dict, List, Any]:
        if not self.subscription:
            return self.components
        elif isinstance(self.subscription, list):
            if isinstance(self.subscription[0], int) and isinstance(self.components, list):
                return [self.components[subscription] for subscription in self.subscription]
            elif isinstance(self.subscription[0], str) and isinstance(self.components, Mapping):
                return {subscription: self.components[subscription] for subscription in self.subscription}
        else:
            return self.components[self.subscription]


@dataclass
class ComponentConstructable(ABC):
    component_identifier: str = ""
    constructed: Any = None
    requirements: Dict[str, Requirement] = field(default_factory=dict)

    def construct(self):
        if self.constructed is None:
            self.constructed = self._construct_impl()
        return self.constructed

    @abstractmethod
    def _construct_impl():
        raise NotImplementedError

    def get_requirement(self, name: str) -> List[Any]:
        return self.requirements[name].get_subscription()

    def get_requirements(self) -> Dict[str, Any]:
        requirement_keys = list(self.requirements.keys())
        return {req_key: self.get_requirement(req_key) for req_key in requirement_keys}

    def has_requirement(self, name: str) -> bool:
        return name in self.requirements


@dataclass
class DatasetRepositoryConstructable(ComponentConstructable):
    storage_connector_path: str = ""

    def _construct_impl(self) -> DatasetRepository:
        dataset_repository: DatasetRepository = DatasetRepository()
        storage_connector = StorageConnectorFactory.get_file_storage_connector(self.storage_connector_path)
        dataset_repository.register("mnist", MNISTFactory(storage_connector))
        return dataset_repository


@dataclass
class DatasetIteratorConstructable(ComponentConstructable):
    dataset_identifier: str = ""
    split_configs: Dict[str, Any] = field(default_factory=dict)

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_repository = self.get_requirement("repository")
        dataset_dict = {}
        for split_config in self.split_configs:
            split_name = split_config["split"]
            iterator, iterator_meta = dataset_repository.get(self.dataset_identifier, split_config)
            dataset_meta = MetaFactory.get_dataset_meta(identifier=self.component_identifier,
                                                        dataset_name=self.dataset_identifier,
                                                        dataset_tag=split_name,
                                                        iterator_meta=iterator_meta)
            dataset_dict[split_name] = ModelGymInformedIteratorFactory.get_dataset_iterator(iterator, dataset_meta)
        return dataset_dict


@dataclass
class DatasetIteratorSplitsConstructable(ComponentConstructable):
    split_configs: Dict = None
    seed: int = 1
    stratified: bool = False

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        splitted_iterators_dict = ModelGymInformedIteratorFactory.get_splitted_iterators(
            self.component_identifier, dataset_iterators_dict, self.seed, self.stratified, self.split_configs)
        return {**dataset_iterators_dict, **splitted_iterators_dict}


@dataclass
class CombinedDatasetIteratorConstructable(ComponentConstructable):
    combine_configs: Dict = None

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_iterators = self.get_requirements()
        combined_iterators_dict = ModelGymInformedIteratorFactory.get_combined_iterators(self.component_identifier,
                                                                                         dataset_iterators,
                                                                                         self.combine_configs)
        return combined_iterators_dict


@dataclass
class InMemoryDatasetIteratorConstructable(ComponentConstructable):

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_in_memory_iterator(self.component_identifier, iterator)
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class FilteredLabelsIteratorConstructable(ComponentConstructable):
    filtered_labels: List[Any] = field(default_factory=list)
    applicable_splits: List[str] = field(default_factory=list)

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_filtered_labels_iterator(self.component_identifier, iterator, self.filtered_labels)
                if name in self.applicable_splits else iterator
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class IteratorViewConstructable(ComponentConstructable):
    split_indices: Dict[str, List[int]] = field(default_factory=dict)
    view_tags: Dict[str, Any] = field(default_factory=dict)
    applicable_split: str = ""

    @staticmethod
    def sample_selection_fun(iterator: DatasetIteratorIF, split_indices: Dict[str, List[int]]) -> List[int]:
        return split_indices

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterator = self.get_requirement("iterators")[self.applicable_split]
        iterator_views = {}
        for name, indices in self.split_indices.items():
            partial_selection_fun = partial(IteratorViewConstructable.sample_selection_fun, split_indices=indices)
            iterator_view = ModelGymInformedIteratorFactory.get_iterator_view(self.component_identifier, dataset_iterator,
                                                                              partial_selection_fun, self.view_tags)
            iterator_views[name] = iterator_view
        return iterator_views


@dataclass
class MappedLabelsIteratorConstructable(ComponentConstructable):
    mappings: Dict[str, Union[List[int], int]] = field(default_factory=dict)
    applicable_splits: List[str] = field(default_factory=list)

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_mapped_labels_iterator(self.component_identifier, iterator, self.mappings)
                if name in self.applicable_splits else iterator
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class FeatureEncodedIteratorConstructable(ComponentConstructable):
    applicable_splits: List[str] = field(default_factory=list)
    feature_encoding_configs: Dict = field(default_factory=Dict)

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        feature_encoded_iterators = ModelGymInformedIteratorFactory.get_feature_encoded_iterators(
            self.component_identifier, dataset_iterators_dict, self.feature_encoding_configs)
        return {name: iterator for name, iterator in feature_encoded_iterators.items() if name in self.applicable_splits}


@dataclass
class OneHotEncodedTargetsIteratorConstructable(ComponentConstructable):
    applicable_splits: List[str] = field(default_factory=list)
    target_vector_size: int = 0

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        one_hot_encoded_target_iterators = ModelGymInformedIteratorFactory.get_one_hot_encoded_target_iterators(
            self.component_identifier, dataset_iterators_dict, self.target_vector_size)
        return {name: iterator for name, iterator in one_hot_encoded_target_iterators.items() if name in self.applicable_splits}


@dataclass
class DataCollatorConstructable(ComponentConstructable):
    collator_params: Dict = field(default_factory=Dict)
    collator_type: Type[CollatorIF] = None

    def _construct_impl(self) -> Callable:
        return self.collator_type(**self.collator_params)


@dataclass
class DataLoadersConstructable(ComponentConstructable):
    batch_size: int = 1
    weigthed_sampling_split_name: str = None

    def _construct_impl(self) -> DatasetLoader:
        dataset_iterators_dict = self.get_requirement("iterators")
        collator: CollatorIF = self.get_requirement("data_collator")
        return DatasetLoaderFactory.get_splitted_data_loaders(dataset_splits=dataset_iterators_dict,
                                                              batch_size=self.batch_size,
                                                              collate_fn=collator,
                                                              weigthed_sampling_split_name=self.weigthed_sampling_split_name)


@dataclass
class ExperimentInfoConstructable(ComponentConstructable):
    log_dir: str = ""
    grid_search_id: str = ""
    run_id: str = ""
    model_name: str = ""

    def _construct_impl(self):
        return DashifyLogger.create_new_experiment(log_dir=self.log_dir,
                                                   subfolder_id=self.grid_search_id,
                                                   model_name=self.model_name,
                                                   dataset_name="",  # TODO fix ugly hack
                                                   run_id=self.run_id)


@dataclass
class OptimizerConstructable(ComponentConstructable):
    optimizer_key: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

    def _construct_impl(self):
        return OptimizerFactory.get_partial_optimizer(self.optimizer_key, self.params)


@dataclass
class ModelRegistryConstructable(ComponentConstructable):
    model_registry: ClassRegistry = None

    def _construct_impl(self):
        self.model_registry = ClassRegistry()
        return self.model_registry


@dataclass
class LossFunctionRegistryConstructable(ComponentConstructable):
    class LossKeys:
        LPLoss = "LPLoss"
        LPLossScaled = "LPLossScaled"
        CrossEntropyLoss = "CrossEntropyLoss"
        BCEWithLogitsLoss = "BCEWithLogitsLoss"
        NLLLoss = "NLLLoss"

    def _construct_impl(self):
        loss_fun_registry = ClassRegistry()
        default_mapping: Dict[str, Loss] = {
            LossFunctionRegistryConstructable.LossKeys.LPLoss: LossFactory.get_lp_loss,
            LossFunctionRegistryConstructable.LossKeys.LPLossScaled: LossFactory.get_scaled_lp_loss,
            LossFunctionRegistryConstructable.LossKeys.BCEWithLogitsLoss: LossFactory.get_bce_with_logits_loss,
            LossFunctionRegistryConstructable.LossKeys.CrossEntropyLoss: LossFactory.get_cross_entropy_loss,
            LossFunctionRegistryConstructable.LossKeys.NLLLoss: LossFactory.get_nll_loss
        }
        for key, loss_type in default_mapping.items():
            loss_fun_registry.add_class(key, loss_type)

        return loss_fun_registry


@dataclass
class MetricFunctionRegistryConstructable(ComponentConstructable):
    class MetricKeys:
        F1_SCORE = "F1_SCORE"
        RECALL = "RECALL"
        PRECISION = "PRECISION"
        AUROC = "AUROC"
        AUPR = "AUPR"
        BRIER_SCORE = "BRIER_SCORE"
        EXPECTED_CALIBRATION_ERROR = "EXPECTED_CALIBRATION_ERROR"
        BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR = "BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR"

    def _construct_impl(self):
        metric_fun_registry = ClassRegistry()
        default_mapping: Dict[str, Metric] = {
            MetricFunctionRegistryConstructable.MetricKeys.F1_SCORE:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.F1_SCORE,
                                                 metric_fun=f1_score),
            MetricFunctionRegistryConstructable.MetricKeys.RECALL:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.RECALL,
                                                 metric_fun=recall_score),
            MetricFunctionRegistryConstructable.MetricKeys.PRECISION:
            MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.PRECISION,
                                             metric_fun=precision_score),
            MetricFunctionRegistryConstructable.MetricKeys.AUROC:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.AUROC,
                                                 metric_fun=binary_auroc_score),
            MetricFunctionRegistryConstructable.MetricKeys.AUPR:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.AUPR,
                                                 metric_fun=binary_aupr_score),
            MetricFunctionRegistryConstructable.MetricKeys.BRIER_SCORE:
                MetricFactory.get_brier_score_metric_fun,
            MetricFunctionRegistryConstructable.MetricKeys.EXPECTED_CALIBRATION_ERROR:
                MetricFactory.get_expected_calibration_error_metric_fun,
            MetricFunctionRegistryConstructable.MetricKeys.BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR:
                MetricFactory.get_binary_classwise_expected_calibration_error_metric_fun
        }
        for key, metric_type in default_mapping.items():
            metric_fun_registry.add_class(key, metric_type)

        return metric_fun_registry


@dataclass
class PredictionPostProcessingRegistryConstructable(ComponentConstructable):
    class FunctionKeys:
        SOFT_MAX = "SOFT_MAX"
        ARG_MAX = "ARG_MAX"
        SIGMOIDAL = "SIGMOIDAL"
        BINARIZATION = "BINARIZATION"
        DUMMY = "DUMMY"

    def _construct_impl(self):
        postprocessing_fun_registry = ClassRegistry()
        default_mapping: Dict[str, PredictPostProcessingIF] = {
            PredictionPostProcessingRegistryConstructable.FunctionKeys.SOFT_MAX: SoftmaxPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.ARG_MAX: ArgmaxPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.SIGMOIDAL: SigmoidalPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.BINARIZATION: BinarizationPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.DUMMY: DummyPostProcessorImpl
        }
        for key, postprocessing_type in default_mapping.items():
            postprocessing_fun_registry.add_class(key, postprocessing_type)
        return postprocessing_fun_registry


@dataclass
class ModelConstructable(ComponentConstructable):
    model_type: str = ""
    model_definition: Dict[str, Any] = field(default_factory=dict)
    seed: int = 0
    prediction_publication_keys: Dict[str, str] = field(default_factory=dict)

    def _construct_impl(self) -> NNModel:
        model_type = self.get_requirement("model_registry")
        return model_type(seed=self.seed, **self.model_definition, **self.prediction_publication_keys)


@dataclass
class TrainComponentConstructable(ComponentConstructable):
    loss_fun_config: Dict = field(default_factory=dict)
    post_processors_config: List[Dict] = field(default_factory=list)
    show_progress: bool = False

    def _construct_impl(self) -> TrainComponent:
        prediction_post_processing_registry: ClassRegistry = self.get_requirement("prediction_postprocessing_registry")
        loss_function_registry: ClassRegistry = self.get_requirement("loss_function_registry")
        train_loss_fun = loss_function_registry.get_instance(**self.loss_fun_config)
        postprocessors = [PredictPostProcessing(prediction_post_processing_registry.get_instance(**config))
                          for config in self.post_processors_config]
        inference_component = InferenceComponent(postprocessors, no_grad=False)
        train_component = TrainComponent(inference_component, train_loss_fun, self.show_progress)
        return train_component


@dataclass
class TrainerConstructable(ComponentConstructable):

    def _construct_impl(self) -> Trainer:
        train_loader: DatasetLoader = self.get_requirement("data_loaders")
        train_component: TrainComponent = self.get_requirement("train_component")
        trainer = Trainer(train_component=train_component, train_loader=train_loader, verbose=True)
        return trainer


@dataclass
class EvalComponentConstructable(ComponentConstructable):
    train_split_name: str = ""
    metrics_config: List = field(default_factory=list)
    loss_funs_config: List = field(default_factory=list)
    post_processors_config: List[Dict] = field(default_factory=list)
    show_progress: bool = False
    cpu_target_subscription_keys: List[str] = field(default_factory=list)
    cpu_prediction_subscription_keys: List[str] = field(default_factory=list)

    def _construct_impl(self) -> Evaluator:
        dataset_loaders: Dict[str, DatasetLoader] = self.get_requirement("data_loaders")
        loss_function_registry: ClassRegistry = self.get_requirement("loss_function_registry")
        metric_registry: ClassRegistry = self.get_requirement("metric_registry")
        prediction_post_processing_registry: ClassRegistry = self.get_requirement("prediction_postprocessing_registry")

        loss_funs = {conf["tag"]: loss_function_registry.get_instance(**conf) for conf in self.loss_funs_config}
        metric_funs = [metric_registry.get_instance(**conf) for conf in self.metrics_config]
        postprocessors = [PredictPostProcessing(prediction_post_processing_registry.get_instance(**config))
                          for config in self.post_processors_config]
        inference_component = InferenceComponent(postprocessors, no_grad=True)
        eval_component = EvalComponent(inference_component, metric_funs, loss_funs, dataset_loaders, self.train_split_name,
                                       self.show_progress, self.cpu_target_subscription_keys, self.cpu_prediction_subscription_keys)
        return eval_component


@dataclass
class EvaluatorConstructable(ComponentConstructable):

    def _construct_impl(self) -> Evaluator:
        eval_component: EvalComponent = self.get_requirement("eval_component")
        evaluator = Evaluator(eval_component)
        return evaluator
