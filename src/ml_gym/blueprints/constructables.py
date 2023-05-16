from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union, Type
from data_stack.dataset.iterator import DatasetIteratorIF
from data_stack.repository.repository import DatasetRepository
from abc import abstractmethod, ABC
from data_stack.io.storage_connectors import StorageConnectorFactory
from data_stack.mnist.factory import MNISTFactory
from ml_gym.data_handling.dataset_loader import DatasetLoader, DatasetLoaderFactory
from ml_gym.early_stopping.early_stopping_strategies import EarlyStoppingIF, EarlyStoppingStrategyFactory
from ml_gym.gym.evaluators.accelerate_evaluator import AccelerateEvalComponent, AccelerateEvaluator
from ml_gym.gym.trainers.accelerate_trainer import AccelerateTrainComponent, AccelerateTrainer
from ml_gym.optimizers.lr_scheduler_factory import LRSchedulerFactory
from ml_gym.optimizers.lr_schedulers import LRSchedulerAdapter
from ml_gym.optimizers.optimizer import OptimizerAdapter, OptimizerBundle
from ml_gym.optimizers.optimizer_factory import OptimizerFactory
from ml_gym.models.nn.net import NNModel
from collections.abc import Mapping
from ml_gym.registries.class_registry import ClassRegistry
from ml_gym.gym.trainers.standard_trainer import Trainer, TrainComponent, InferenceComponent
from ml_gym.loss_functions.loss_functions import Loss
from sklearn.metrics import f1_score, recall_score, precision_score, accuracy_score, balanced_accuracy_score
from ml_gym.metrics.metrics import Metric, binary_aupr_score, binary_auroc_score
from ml_gym.metrics.metric_factory import MetricFactory
from ml_gym.gym.evaluators.evaluator import Evaluator, EvalComponent
from ml_gym.data_handling.postprocessors.factory import ModelGymInformedIteratorFactory
from ml_gym.data_handling.postprocessors.collator import Collator
from ml_gym.gym.post_processing import PredictPostProcessingIF, SoftmaxPostProcessorImpl, \
    ArgmaxPostProcessorImpl, SigmoidalPostProcessorImpl, DummyPostProcessorImpl, PredictPostProcessing, \
    BinarizationPostProcessorImpl, MaxOrMinPostProcessorImpl
from data_stack.dataset.meta import MetaFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from functools import partial
from ml_gym.loss_functions.loss_factory import LossFactory
import warnings
from ml_gym.checkpointing.checkpoint_factory import CheckpointingStrategyFactory
from ml_gym.checkpointing.checkpointing import CheckpointingIF


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
    """
    ComponentConstructable is an Abstract class which is used to create all the other constructable calsses.
    The abstract class allows the other Constructables to maintain a common single structure to be used to access the classes.
    """
    component_identifier: str = ""
    constructed: Any = None
    requirements: Dict[str, Requirement] = field(default_factory=dict)

    def construct(self):
        if self.constructed is None:
            self.constructed = self._construct_impl()
        return self.constructed

    @abstractmethod
    def _construct_impl(self):
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
    """
    DatasetRepositoryConstructable class initializes DatasetRepository & StorageConnectorFactory object from datastack library
    to be used for accessing data for models used in MlGym.
    """
    storage_connector_path: str = ""

    def _construct_impl(self) -> DatasetRepository:
        dataset_repository: DatasetRepository = DatasetRepository()
        storage_connector = StorageConnectorFactory.get_file_storage_connector(self.storage_connector_path)
        dataset_repository.register("mnist", MNISTFactory(storage_connector))
        return dataset_repository


@dataclass
class DatasetIteratorConstructable(ComponentConstructable):
    """
    DatasetIteratorConstructable class is used to make the dataset iterable
    to be used for accessing specific split for models used in MlGym.
    """
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
    """
    DatasetIteratorSplitsConstructable class is used to make the dataset iterable.
    to be used for accessing all data splits for models used in MlGym.
    """
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
    """
    CombinedDatasetIteratorConstructable class is used to get combined itterators for the dataset by 
    combining iterators from old splits and getting new iterators for new splits.
    """
    combine_configs: Dict = None

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_iterators = self.get_requirements()
        combined_iterators_dict = ModelGymInformedIteratorFactory.get_combined_iterators(self.component_identifier,
                                                                                         dataset_iterators,
                                                                                         self.combine_configs)
        return combined_iterators_dict


@dataclass
class InMemoryDatasetIteratorConstructable(ComponentConstructable):
    """
    InMemoryDatasetIteratorConstructable class is used to load a given iterator into memory to speed up the iteration.
    """
    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_in_memory_iterator(self.component_identifier, iterator)
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class ShuffledDatasetIteratorConstructable(ComponentConstructable):
    """
    ShuffledDatasetIteratorConstructable class is used to get randomly shuffled iterators usefull for large datasets.
    """
    seeds: Dict[str, Any] = field(default_factory=dict)
    applicable_splits: List[str] = field(default_factory=list)

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_shuffled_iterator(self.component_identifier, iterator, self.seeds[name])
                if name in self.applicable_splits else iterator
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class FilteredLabelsIteratorConstructable(ComponentConstructable):
    """
    FilteredLabelsIteratorConstructable class is used to get an iterator which can iterate through filtered labels in the dataset.
    """
    filtered_labels: List[Any] = field(default_factory=list)
    applicable_splits: List[str] = field(default_factory=list)

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_filtered_labels_iterator(self.component_identifier, iterator, self.filtered_labels)
                if name in self.applicable_splits else iterator
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class IteratorViewConstructable(ComponentConstructable):
    """
    IteratorViewConstructable class is used to create a view on an iterator for accessing elements of a given split only.
    """
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
    """
    MappedLabelsIteratorConstructable class is used to get an iterator which can iterate through mapped labels in the dataset.
    """
    mappings: Dict[str, Union[List[int], int]] = field(default_factory=dict)
    applicable_splits: List[str] = field(default_factory=list)

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        return {name: ModelGymInformedIteratorFactory.get_mapped_labels_iterator(self.component_identifier, iterator, self.mappings)
                if name in self.applicable_splits else iterator
                for name, iterator in dataset_iterators_dict.items()}


@dataclass
class FeatureEncodedIteratorConstructable(ComponentConstructable):
    """
    FeatureEncodedIteratorConstructable class is used to get an iterator which can iterate through encoded fetures of a dataset.
    """
    applicable_splits: List[str] = field(default_factory=list)
    feature_encoding_configs: Dict = field(default_factory=Dict)

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        feature_encoded_iterators = ModelGymInformedIteratorFactory.get_feature_encoded_iterators(
            self.component_identifier, dataset_iterators_dict, self.feature_encoding_configs)
        return {name: iterator for name, iterator in feature_encoded_iterators.items() if name in self.applicable_splits}


@dataclass
class OneHotEncodedTargetsIteratorConstructable(ComponentConstructable):
    """
    OneHotEncodedTargetsIteratorConstructable class is used to get an iterator which can iterate 
    through one hot encoded targets of a dataset.
    """
    applicable_splits: List[str] = field(default_factory=list)
    target_vector_size: int = 0

    def _construct_impl(self) -> Dict[str, DatasetIteratorIF]:
        dataset_iterators_dict = self.get_requirement("iterators")
        one_hot_encoded_target_iterators = ModelGymInformedIteratorFactory.get_one_hot_encoded_target_iterators(
            self.component_identifier, dataset_iterators_dict, self.target_vector_size)
        return {name: iterator for name, iterator in one_hot_encoded_target_iterators.items() if name in self.applicable_splits}


@dataclass
class DataCollatorConstructable(ComponentConstructable):
    """
    DataCollatorConstructable class is used to collate data for TrainBatch
    TO DO.
    """
    collator_params: Dict = field(default_factory=Dict)
    collator_type: Type[Collator] = None

    def _construct_impl(self) -> Callable:
        return self.collator_type(**self.collator_params)


@dataclass
class DeprecatedDataLoadersConstructable(ComponentConstructable):
    """
    DeprecatedDataLoadersConstructable class is used to get the spliited data based on the wighted sampling. (DEPRECATED)
    """
    batch_size: int = 1
    weigthed_sampling_split_name: str = None
    label_pos: int = 2
    seeds: Dict[str, int] = field(default_factory=dict)
    drop_last: bool = False

    def _construct_impl(self) -> DatasetLoader:
        warnings.warn(message="Future DataLoader interface change. Expects sampling strategy in the future.", category=FutureWarning)
        dataset_iterators_dict = self.get_requirement("iterators")
        collator: Collator = self.get_requirement("data_collator")
        return DatasetLoaderFactory.get_splitted_data_loaders_deprecated(dataset_splits=dataset_iterators_dict,
                                                                         batch_size=self.batch_size,
                                                                         collate_fn=collator,
                                                                         weigthed_sampling_split_name=self.weigthed_sampling_split_name,
                                                                         label_pos=self.label_pos,
                                                                         seeds=self.seeds,
                                                                         drop_last=self.drop_last)


@dataclass
class DataLoadersConstructable(ComponentConstructable):
    """
    DataLoadersConstructable class is used to get the spliited data based on the sampling stratergy.
    """
    batch_size: int = 1
    sampling_strategies: Dict[str, Any] = field(default_factory=dict)
    drop_last: bool = False

    def _construct_impl(self) -> DatasetLoader:
        dataset_iterators_dict = self.get_requirement("iterators")
        collator: Collator = self.get_requirement("data_collator")
        return DatasetLoaderFactory.get_splitted_data_loaders(dataset_splits=dataset_iterators_dict,
                                                              batch_size=self.batch_size,
                                                              collate_fn=collator,
                                                              sampling_strategies=self.sampling_strategies,
                                                              drop_last=self.drop_last)


@dataclass
class OptimizerConstructable(ComponentConstructable):
    """
    OptimizerConstructable class is used to create an object of Optimizer Adapter based on what optimizer is
    to be used as per the config of MlGym Job.
    """
    optimizer_key: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

    def _construct_impl(self) -> OptimizerAdapter:
        return OptimizerFactory.get_optimizer(self.optimizer_key, self.params)


@dataclass
class LRSchedulerConstructable(ComponentConstructable):
    """
    LRSchedulerConstructable class is used to create an object of LRScheduler Adapter based on what shedule of learning rate is
    to be used as per the config of MlGym Job.
    """
    lr_scheduler_key: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

    def _construct_impl(self) -> LRSchedulerAdapter:
        return LRSchedulerFactory.get_lr_scheduler(self.lr_scheduler_key, self.params)


@dataclass
class OptimizerBundleConstructable(ComponentConstructable):
    """
    OptimizerBundleConstructable class is used to create an object of Optimizer Bundle containing
    all optimizers with registered optimizer params.
    """

    optimizers_config: Dict[str, Any] = field(default_factory=list)
    # {
    #     "o_1": {"optimizer_key": "ADAM", "params": {"lr": 1, "momentum": 0.9}},
    #     "o_2": {"optimizer_key": "SGD", "params": {"lr": 2, "momentum": 0.8}}
    # }

    optimizer_key_to_param_key_filters: Dict[str, Any] = field(default_factory=dict)
    # {
    #     "o_1": ["encoder_1", "encoder_2"],
    #     "o_2": ["bias"]
    # }

    def _construct_impl(self) -> OptimizerAdapter:
        optimizers = {optimizer_id: OptimizerFactory.get_optimizer(**optimizer_config)
                      for optimizer_id, optimizer_config in self.optimizers_config.items()}
        return OptimizerBundle(optimizers=optimizers, optimizer_key_to_param_key_filters=self.optimizer_key_to_param_key_filters)


@dataclass
class ModelRegistryConstructable(ComponentConstructable):
    """
    ModelRegistryConstructable class is used to create a ClassRegistry object for model.
    """
    model_registry: ClassRegistry = None

    def _construct_impl(self):
        self.model_registry = ClassRegistry()
        return self.model_registry


@dataclass
class LossFunctionRegistryConstructable(ComponentConstructable):
    """
    LossFunctionRegistryConstructable class is used to create a ClassRegistry object for all available Loss Functions.
    """
    class LossKeys:
        LPLoss = "LPLoss"
        LPPredictionLoss = "LPPredictionLoss"
        # LPLossScaled = "LPLossScaled"
        CrossEntropyLoss = "CrossEntropyLoss"
        BCEWithLogitsLoss = "BCEWithLogitsLoss"
        BCELoss = "BCELoss"
        NLLLoss = "NLLLoss"

    def _construct_impl(self):
        loss_fun_registry = ClassRegistry()
        default_mapping: Dict[str, Loss] = {
            LossFunctionRegistryConstructable.LossKeys.LPLoss: LossFactory.get_lp_loss,
            LossFunctionRegistryConstructable.LossKeys.LPPredictionLoss: LossFactory.get_lp_loss,  # TODO this is legacy for DAE results from June 2021
            # LossFunctionRegistryConstructable.LossKeys.LPLossScaled: LossFactory.get_scaled_lp_loss,
            LossFunctionRegistryConstructable.LossKeys.BCEWithLogitsLoss: LossFactory.get_bce_with_logits_loss,
            LossFunctionRegistryConstructable.LossKeys.BCELoss: LossFactory.get_bce_loss,
            LossFunctionRegistryConstructable.LossKeys.CrossEntropyLoss: LossFactory.get_cross_entropy_loss,
            LossFunctionRegistryConstructable.LossKeys.NLLLoss: LossFactory.get_nll_loss
        }
        for key, loss_type in default_mapping.items():
            loss_fun_registry.add_class(key, loss_type)

        return loss_fun_registry


@dataclass
class MetricFunctionRegistryConstructable(ComponentConstructable):
    """
    MetricFunctionRegistryConstructable class is used to create a ClassRegistry object for all available Evaluation Metrics.
    """
    class MetricKeys:
        F1_SCORE = "F1_SCORE"
        ACCURACY = "ACCURACY"
        BALANCED_ACCURACY = "BALANCED_ACCURACY"
        RECALL = "RECALL"
        PRECISION = "PRECISION"
        AUROC = "AUROC"
        AUPR = "AUPR"
        RECALL_AT_K = "RECALL_AT_K"
        AREA_UNDER_RECALL_AT_K = "AREA_UNDER_RECALL_AT_K"
        BRIER_SCORE = "BRIER_SCORE"
        EXPECTED_CALIBRATION_ERROR = "EXPECTED_CALIBRATION_ERROR"
        BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR = "BINARY_CLASSWISE_EXPECTED_CALIBRATION_ERROR"

    def _construct_impl(self):
        metric_fun_registry = ClassRegistry()
        default_mapping: Dict[str, Metric] = {
            MetricFunctionRegistryConstructable.MetricKeys.F1_SCORE:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.F1_SCORE,
                                                 metric_fun=f1_score),
            MetricFunctionRegistryConstructable.MetricKeys.ACCURACY:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.ACCURACY,
                                                 metric_fun=accuracy_score),
            MetricFunctionRegistryConstructable.MetricKeys.BALANCED_ACCURACY:
                MetricFactory.get_sklearn_metric(metric_key=MetricFunctionRegistryConstructable.MetricKeys.BALANCED_ACCURACY,
                                                 metric_fun=balanced_accuracy_score),
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
            MetricFunctionRegistryConstructable.MetricKeys.RECALL_AT_K:
                MetricFactory.get_recall_at_k_metric_fun,
            MetricFunctionRegistryConstructable.MetricKeys.AREA_UNDER_RECALL_AT_K:
                MetricFactory.get_area_under_recall_at_k_metric_fun,
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
    """
    PredictionPostProcessingRegistryConstructable class is used to create a ClassRegistry object for 
    all available Prediction Functions used in post processing.
    """
    class FunctionKeys:
        SOFT_MAX = "SOFT_MAX"
        ARG_MAX = "ARG_MAX"
        MIN_OR_MAX = "MIN_OR_MAX"
        SIGMOIDAL = "SIGMOIDAL"
        BINARIZATION = "BINARIZATION"
        DUMMY = "DUMMY"

    def _construct_impl(self):
        postprocessing_fun_registry = ClassRegistry()
        default_mapping: Dict[str, PredictPostProcessingIF] = {
            PredictionPostProcessingRegistryConstructable.FunctionKeys.SOFT_MAX: SoftmaxPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.ARG_MAX: ArgmaxPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.MIN_OR_MAX: MaxOrMinPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.SIGMOIDAL: SigmoidalPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.BINARIZATION: BinarizationPostProcessorImpl,
            PredictionPostProcessingRegistryConstructable.FunctionKeys.DUMMY: DummyPostProcessorImpl
        }
        for key, postprocessing_type in default_mapping.items():
            postprocessing_fun_registry.add_class(key, postprocessing_type)
        return postprocessing_fun_registry


@dataclass
class ModelConstructable(ComponentConstructable):
    """
    ModelConstructable class is used to construct a Neural Net model based on the
    params in the model registry.
    """
    model_type: str = ""
    model_definition: Dict[str, Any] = field(default_factory=dict)
    seed: int = None
    prediction_publication_keys: Dict[str, str] = field(default_factory=dict)

    def _construct_impl(self) -> NNModel:
        other_params = {"seed": self.seed} if self.seed is not None else {}
        model_type = self.get_requirement("model_registry")
        return model_type(**other_params, **self.model_definition, **self.prediction_publication_keys)


@dataclass
class TrainComponentConstructable(ComponentConstructable):
    """
    TrainComponentConstructable class is used to construct a TrainComponent
    used when there is only one CPU or GPU to train model.
    """
    loss_fun_config: Dict = field(default_factory=dict)
    post_processors_config: List[Dict] = field(default_factory=list)
    show_progress: bool = False

    def _construct_impl(self) -> TrainComponent:
        prediction_post_processing_registry: ClassRegistry = self.get_requirement("prediction_postprocessing_registry")
        loss_function_registry: ClassRegistry = self.get_requirement("loss_function_registry")
        train_loss_fun = loss_function_registry.get_instance(**self.loss_fun_config)
        postprocessors = [PredictPostProcessing(prediction_post_processing_registry.get_instance(config["key"], **config["params"]))
                          for config in self.post_processors_config]

        inference_component = InferenceComponent(no_grad=False)
        train_component = TrainComponent(inference_component, postprocessors, train_loss_fun)
        return train_component


@dataclass
class AccelerateTrainComponentConstructable(ComponentConstructable):
    """
    AccelerateTrainComponentConstructable class is used to construct a AccelerateTrainComponent
    used when there are multiple GPUs to train model.
    """
    loss_fun_config: Dict = field(default_factory=dict)
    post_processors_config: List[Dict] = field(default_factory=list)

    def _construct_impl(self) -> AccelerateTrainComponent:
        prediction_post_processing_registry: ClassRegistry = self.get_requirement("prediction_postprocessing_registry")
        loss_function_registry: ClassRegistry = self.get_requirement("loss_function_registry")
        train_loss_fun = loss_function_registry.get_instance(**self.loss_fun_config)
        postprocessors = [PredictPostProcessing(prediction_post_processing_registry.get_instance(config["key"], **config["params"]))
                          for config in self.post_processors_config]

        inference_component = InferenceComponent(no_grad=False)
        train_component = AccelerateTrainComponent(inference_component, postprocessors, train_loss_fun)
        return train_component


@dataclass
class TrainerConstructable(ComponentConstructable):
    """
    TrainerConstructable creates a Trainer object containing functions used to train the torch Neural Net model on CPU.
    """
    def _construct_impl(self) -> Trainer:
        train_loader: DatasetLoader = self.get_requirement("data_loaders")
        train_component: TrainComponent = self.get_requirement("train_component")
        trainer = Trainer(train_component=train_component, train_loader=train_loader)
        return trainer


@dataclass
class AccelerateTrainerConstructable(ComponentConstructable):
    """
    AccelerateTrainerConstructable creates a AccelerateTrainer object containing functions 
    used to train the torch Neural Net model on GPU.
    """
    def _construct_impl(self) -> AccelerateTrainer:
        train_loader: DatasetLoader = self.get_requirement("data_loaders")
        train_component: TrainComponent = self.get_requirement("train_component")
        trainer = AccelerateTrainer(train_component=train_component, train_loader=train_loader)
        return trainer


@dataclass
class EvalComponentConstructable(ComponentConstructable):
    """
    EvalComponentConstructable creates a EvalComponent object containing functions 
    used to evaluate the torch Neural Net model on CPU.
    """
    metrics_config: List = field(default_factory=list)
    loss_funs_config: List = field(default_factory=list)
    post_processors_config: List[Dict] = field(default_factory=list)
    show_progress: bool = False
    cpu_target_subscription_keys: List[str] = field(default_factory=list)
    cpu_prediction_subscription_keys: List[str] = field(default_factory=list)
    metrics_computation_config: List[Dict] = None
    loss_computation_config: List[Dict] = None

    def _construct_impl(self) -> EvalComponent:
        dataset_loaders: Dict[str, DatasetLoader] = self.get_requirement("data_loaders")
        loss_function_registry: ClassRegistry = self.get_requirement("loss_function_registry")
        metric_registry: ClassRegistry = self.get_requirement("metric_registry")
        prediction_post_processing_registry: ClassRegistry = self.get_requirement("prediction_postprocessing_registry")

        loss_funs = {conf["tag"]: loss_function_registry.get_instance(**conf) for conf in self.loss_funs_config}
        metric_funs = [metric_registry.get_instance(**conf) for conf in self.metrics_config]

        postprocessors_dict = defaultdict(list)
        for config in self.post_processors_config:
            if "applicable_splits" in config:
                for split in config["applicable_splits"]:
                    postprocessors_dict[split].append(PredictPostProcessing(
                        prediction_post_processing_registry.get_instance(config["key"], **config["params"])))
            else:
                if "params" in config:
                    postprocessors_dict["default"].append(PredictPostProcessing(
                        prediction_post_processing_registry.get_instance(config["key"], **config["params"])))
                else:  # TODO this is the legacy version!
                    postprocessors_dict["default"].append(PredictPostProcessing(prediction_post_processing_registry.get_instance(**config)))

        inference_component = InferenceComponent(no_grad=True)
        eval_component = EvalComponent(inference_component, postprocessors_dict, metric_funs, loss_funs, dataset_loaders,
                                       self.show_progress, self.cpu_target_subscription_keys, self.cpu_prediction_subscription_keys,
                                       self.metrics_computation_config, self.loss_computation_config)
        return eval_component


@dataclass
class EvaluatorConstructable(ComponentConstructable):
    """
    EvaluatorConstructable creates a Evaluator object containing functions 
    used to evaluate the torch Neural Net model on CPU.
    """
    def _construct_impl(self) -> Evaluator:
        eval_component: EvalComponent = self.get_requirement("eval_component")
        evaluator = Evaluator(eval_component)
        return evaluator


@dataclass
class AccelerateEvalComponentConstructable(ComponentConstructable):
    """
    AccelerateEvalComponentConstructable creates a AccelerateEvalComponent object containing functions 
    used to evaluate the torch Neural Net model on GPU.
    """
    metrics_config: List = field(default_factory=list)
    loss_funs_config: List = field(default_factory=list)
    post_processors_config: List[Dict] = field(default_factory=list)
    cpu_target_subscription_keys: List[str] = field(default_factory=list)
    cpu_prediction_subscription_keys: List[str] = field(default_factory=list)
    metrics_computation_config: List[Dict] = None
    loss_computation_config: List[Dict] = None

    def _construct_impl(self) -> AccelerateEvalComponent:
        dataset_loaders: Dict[str, DatasetLoader] = self.get_requirement("data_loaders")
        loss_function_registry: ClassRegistry = self.get_requirement("loss_function_registry")
        metric_registry: ClassRegistry = self.get_requirement("metric_registry")
        prediction_post_processing_registry: ClassRegistry = self.get_requirement("prediction_postprocessing_registry")

        loss_funs = {conf["tag"]: loss_function_registry.get_instance(**conf) for conf in self.loss_funs_config}
        metric_funs = [metric_registry.get_instance(**conf) for conf in self.metrics_config]

        postprocessors_dict = defaultdict(list)
        for config in self.post_processors_config:
            if "applicable_splits" in config:
                for split in config["applicable_splits"]:
                    postprocessors_dict[split].append(PredictPostProcessing(
                        prediction_post_processing_registry.get_instance(config["key"], **config["params"])))
            else:
                if "params" in config:
                    postprocessors_dict["default"].append(PredictPostProcessing(
                        prediction_post_processing_registry.get_instance(config["key"], **config["params"])))
                else:  # TODO this is the legacy version!
                    postprocessors_dict["default"].append(PredictPostProcessing(prediction_post_processing_registry.get_instance(**config)))

        inference_component = InferenceComponent(no_grad=True)
        eval_component = AccelerateEvalComponent(inference_component, postprocessors_dict, metric_funs, loss_funs, dataset_loaders,
                                                 self.cpu_target_subscription_keys, self.cpu_prediction_subscription_keys,
                                                 self.metrics_computation_config, self.loss_computation_config)
        return eval_component


@dataclass
class AccelerateEvaluatorConstructable(ComponentConstructable):
    """
    AccelerateEvaluatorConstructable creates a AccelerateEvaluator object containing functions 
    used to evaluate the torch Neural Net model on GPU.
    """

    def _construct_impl(self) -> AccelerateEvaluator:
        eval_component: AccelerateEvalComponent = self.get_requirement("eval_component")
        evaluator = AccelerateEvaluator(eval_component)
        return evaluator


@dataclass
class EarlyStoppingRegistryConstructable(ComponentConstructable):
    """
    EarlyStoppingRegistryConstructable creates a ClassRegistry object for all available Early Stopping Stratergies.
    """
    class StrategyKeys:
        LAST_K_EPOCHS_IMPROVEMENT_STRATEGY = "LAST_K_EPOCHS_IMPROVEMENT_STRATEGY"

    def _construct_impl(self):
        strategy_registry = ClassRegistry()
        default_mapping: Dict[str, Metric] = {
            EarlyStoppingRegistryConstructable.StrategyKeys.LAST_K_EPOCHS_IMPROVEMENT_STRATEGY:
                EarlyStoppingStrategyFactory.get_last_k_epochs_improvement_strategy
        }
        for key, metric_type in default_mapping.items():
            strategy_registry.add_class(key, metric_type)

        return strategy_registry


@dataclass
class EarlyStoppingStrategyConstructable(ComponentConstructable):
    """
    EarlyStoppingStrategyConstructable initializes the EarlyStoppingIF  for all available Early Stopping Stratergies.
    """
    early_stopping_config: Dict = field(default_factory=dict)
    early_stopping_key: str = ""

    def _construct_impl(self) -> EarlyStoppingIF:
        early_stopping_registry: ClassRegistry = self.get_requirement("early_stopping_strategy_registry")
        early_stopping_strategy = early_stopping_registry.get_instance(key=self.early_stopping_key, **self.early_stopping_config)
        return early_stopping_strategy


@dataclass
class CheckpointingRegistryConstructable(ComponentConstructable):
    """
    CheckpointingRegistryConstructable creates a ClassRegistry object for all available Checkpointing Stratergies.
    """
    class StrategyKeys:
        SAVE_LAST_EPOCH_ONLY_CHECKPOINTING_STRATEGY = "SAVE_LAST_EPOCH_ONLY_CHECKPOINTING_STRATEGY"
        SAVE_ALL_CHECKPOINTING_STRATEGY = "SAVE_ALL_CHECKPOINTING_STRATEGY"

    def _construct_impl(self) -> ClassRegistry:
        strategy_registry = ClassRegistry()
        default_mapping: Dict[str, Metric] = {
            CheckpointingRegistryConstructable.StrategyKeys.SAVE_LAST_EPOCH_ONLY_CHECKPOINTING_STRATEGY:
            CheckpointingStrategyFactory.get_save_last_epoch_only_checkpointing_strategy,
            CheckpointingRegistryConstructable.StrategyKeys.SAVE_ALL_CHECKPOINTING_STRATEGY:
            CheckpointingStrategyFactory.get_save_all_checkpointing_strategy
        }
        for key, metric_type in default_mapping.items():
            strategy_registry.add_class(key, metric_type)

        return strategy_registry


@dataclass
class CheckpointingStrategyConstructable(ComponentConstructable):
    """
    CheckpointingStrategyConstructable initializes the CheckpointingIF for all available Checkpointing Stratergies.
    """
    checkpointing_config: Dict = field(default_factory=dict)
    checkpointing_key: str = ""

    def _construct_impl(self) -> CheckpointingIF:
        checkpointing_registry: ClassRegistry = self.get_requirement("checkpointing_strategy_registry")
        checkpointing_strategy = checkpointing_registry.get_instance(key=self.checkpointing_key, **self.checkpointing_config)
        return checkpointing_strategy
