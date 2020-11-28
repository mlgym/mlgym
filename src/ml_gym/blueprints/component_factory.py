import copy
from typing import Dict, Any, List, Type
from collections import namedtuple
from dataclasses import dataclass, field
import hashlib
from ml_gym.error_handling.exception import ComponentConstructionError
from ml_gym.blueprints.constructables import ComponentConstructable, DatasetIteratorConstructable, \
    DatasetIteratorSplitsConstructable, Requirement, DataLoadersConstructable, DatasetRepositoryConstructable, \
    OptimizerConstructable, ModelRegistryConstructable, ModelConstructable, LossFunctionRegistryConstructable, \
    MetricFunctionRegistryConstructable, TrainerConstructable, EvaluatorConstructable, MappedLabelsIteratorConstructable, \
    FilteredLabelsIteratorConstructable, FeatureEncodedIteratorConstructable, CombinedDatasetIteratorConstructable, \
    DataCollatorConstructable, PredictionPostProcessingRegistryConstructable, TrainComponentConstructable, EvalComponentConstructable, \
    IteratorViewConstructable


class Injector:

    def __init__(self, mapping: Dict[str, Any]):
        self.mapping = mapping

    def inject_pass(self, component_parameters: Dict) -> Any:
        def inject(parameter: Dict):
            if isinstance(parameter, dict) and "injectable" in parameter:
                return self.mapping[parameter["injectable"]["id"]]
            else:
                return parameter
        return {key: inject(parameter) for key, parameter in component_parameters.items()}


@dataclass
class ComponentRepresentation:
    """ Direct class represenation of components in the config dictionary
    """
    component_type_key: str
    variant_key: str
    config: Dict = field(default_factory=dict)
    name: str = None  # not part of the hash
    requirements: List["RequirementRepresentation"] = field(default_factory=dict)

    @property
    def hash(self) -> str:
        content_string = "" + self.component_type_key + \
            self.variant_key + str(self.config)
        return hashlib.sha256(content_string.encode('utf-8')).hexdigest()

    def __str__(self):
        return f"ComponentRepresentation(name='{self.name}'," \
            f"component_type_key='{self.component_type_key}'," \
            f"variant_key='{self.variant_key}'," \
            f"config={str(self.config)}," \
            f"hash='{self.hash}'," \
            f"requirements={self.requirements}])"

    def __repr__(self):
        return self.__str__()


@dataclass
class RequirementRepresentation:
    """ Class representation of a requirement of a component defined in the config.
    """
    component: ComponentRepresentation
    subscription: List[int]

    @property
    def hash(self) -> str:
        return self.component.hash


class ComponentFactory:
    """
    The component factory builds the machine learning components like dataset iterators, dataset splitters, models, trainers etc.
    Each component type can have multiple variants. This relationship is captured by component_factory_registry and
    ComponentVariantsRegistry. The ComponentFactoryRegistry maps a component_key to a ComponentVariantsRegistry.
    The ComponentVariantsRegistry maps a variant key to the concrete ComponentConstructable.
    """

    class ComponentVariantsRegistry:
        def __init__(self):
            self.constructables: Dict[str, ComponentConstructable] = {}

        def construct(self, variant_key: str, component_name: str, config: Dict[str, Any] = None, requirements: List[Any] = None):
            if config is None:
                config = {}

            try:
                constructable = self.constructables[variant_key]
                component = constructable(component_identifier=component_name, requirements=requirements, **config).construct()
            except Exception as e:
                raise ComponentConstructionError(f"Error during component creation from {constructable}") from e
            return component

        def register_variant(self, variant_key: str, component_constructable_type: Type[ComponentConstructable]):
            self.constructables[variant_key] = component_constructable_type

    def __init__(self, injector: Injector = None):
        self.injector = injector
        ComponentVariant = namedtuple('ComponentVariant', ['component_key',
                                                           'variant_key',
                                                           'component_constructable_type'])
        # register the default components with their variants
        default_component_variants = [
            ComponentVariant("DATASET_REPOSITORY", "DEFAULT", DatasetRepositoryConstructable),
            ComponentVariant("DATASET_ITERATORS", "DEFAULT", DatasetIteratorConstructable),
            ComponentVariant("SPLITTED_DATASET_ITERATORS", "RANDOM", DatasetIteratorSplitsConstructable),
            ComponentVariant("COMBINED_DATASET_ITERATORS", "DEFAULT", CombinedDatasetIteratorConstructable),
            ComponentVariant("FILTERED_LABELS_ITERATOR", "DEFAULT", FilteredLabelsIteratorConstructable),
            ComponentVariant("ITERATOR_VIEW", "DEFAULT", IteratorViewConstructable),
            ComponentVariant("MAPPED_LABELS_ITERATOR", "DEFAULT", MappedLabelsIteratorConstructable),
            ComponentVariant("DATA_COLLATOR", "DEFAULT", DataCollatorConstructable),
            ComponentVariant("FEATURE_ENCODED_ITERATORS", "DEFAULT", FeatureEncodedIteratorConstructable),
            ComponentVariant("DATA_LOADER", "DEFAULT", DataLoadersConstructable),
            ComponentVariant("OPTIMIZER", "DEFAULT", OptimizerConstructable),
            ComponentVariant("MODEL_REGISTRY", "DEFAULT", ModelRegistryConstructable),
            ComponentVariant("LOSS_FUNCTION_REGISTRY", "DEFAULT", LossFunctionRegistryConstructable),
            ComponentVariant("METRIC_REGISTRY", "DEFAULT", MetricFunctionRegistryConstructable),
            ComponentVariant("PREDICTION_POSTPROCESSING_REGISTRY", "DEFAULT", PredictionPostProcessingRegistryConstructable),
            ComponentVariant("MODEL", "DEFAULT", ModelConstructable),
            ComponentVariant("TRAIN_COMPONENT", "DEFAULT", TrainComponentConstructable),
            ComponentVariant("TRAINER", "DEFAULT", TrainerConstructable),
            ComponentVariant("EVAL_COMPONENT", "DEFAULT", EvalComponentConstructable),
            ComponentVariant("EVALUATOR", "DEFAULT", EvaluatorConstructable)
        ]
        self.component_factory_registry: Dict[str, Any] = {}
        for variant in default_component_variants:
            self.register_component_type(*variant)

    def register_component_type(self, component_key: str, variant_key: str, component_constructable_type: Type[ComponentConstructable]):
        if component_key not in self.component_factory_registry:
            component_variants_registry = ComponentFactory.ComponentVariantsRegistry()
            self.component_factory_registry[component_key] = component_variants_registry
        self.component_factory_registry[component_key].register_variant(variant_key, component_constructable_type)

    def _calc_dependency_graph(self, component_config: Dict) -> Dict[str, ComponentRepresentation]:
        """Returns a dict that maps component hash values to components.
        Each component can have requirements which in return are components again.
        Thereby, defining the dependency relationship of components, e.g., trainer depends on model."""

        def create_component_representation(component_config: Dict, component_name: str = None) -> ComponentRepresentation:
            requirements = {}
            if "requirements" in component_config:
                requirements = {}
                for requirement in component_config.pop("requirements"):
                    component_representation = create_component_representation(requirement["component"])
                    req_rep = RequirementRepresentation(component_representation, requirement.get("subscription"))
                    requirements[requirement["name"]] = req_rep
            # inject components
            if self.injector and "config" in component_config:
                component_config["config"] = self.injector.inject_pass(component_config["config"])
            try:
                component_representation = ComponentRepresentation(name=component_name, requirements=requirements, **component_config)
                return component_representation
            except Exception as e:
                raise ComponentConstructionError(
                    f"Error during component representation instantiation. component_name: {component_name}") from e

        component_config = copy.deepcopy(component_config)  # needed because the pop call in the auxilary function is destructive
        component_representations = {}
        for component_name, component_dict in component_config.items():
            component_representation = create_component_representation(component_config=component_dict, component_name=component_name)
            component_representations[component_representation.hash] = component_representation
        return component_representations

    def get_hash_to_component_name_map(self, component_representations: Dict[str, ComponentRepresentation]) -> Dict[str, str]:
        return {hash_key: rep.name for hash_key, rep in component_representations.items()}

    def build_components_from_config(self, component_config: Dict) -> Dict:
        def build_component(component_hash: str, component_representation_graph: Dict[str, ComponentRepresentation], components: Dict[str, Any]):
            component_representation = component_representation_graph[component_hash]
            # build the requirements if not built yet
            for requirement_name, requirement in component_representation.requirements.items():
                if requirement.hash not in components:
                    components = build_component(component_hash, component_representation_graph, components)
            # collect the requirements
            requirements = {name: Requirement(components[requirement.hash], requirement.subscription)
                            for name, requirement in component_representation.requirements.items()}
            # build the requested component
            component_variants_registry = self.component_factory_registry[component_representation.component_type_key]
            component = component_variants_registry.construct(
                component_representation.variant_key, component_representation.name, component_representation.config, requirements)
            components[component_hash] = component
            return components

        # calculate the dependency graph of components
        component_representation_graph = self._calc_dependency_graph(component_config)
        # build each component
        components: Dict[str, Any] = {}  # maps
        for component_hash, component_representation in component_representation_graph.items():
            if component_hash not in components:
                components = build_component(component_hash, component_representation_graph, components)
        hast_to_name_map = self.get_hash_to_component_name_map(component_representation_graph)
        return {hast_to_name_map[hash_value]: component for hash_value, component in components.items()}
