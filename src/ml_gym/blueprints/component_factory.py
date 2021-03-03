import copy
from typing import Dict, Any, List, Optional, Type, Union
from collections import namedtuple
from dataclasses import dataclass, field
from ml_gym.error_handling.exception import ComponentConstructionError
from ml_gym.blueprints.constructables import ComponentConstructable, DatasetIteratorConstructable, \
    DatasetIteratorSplitsConstructable, Requirement, DataLoadersConstructable, DatasetRepositoryConstructable, \
    OptimizerConstructable, ModelRegistryConstructable, ModelConstructable, LossFunctionRegistryConstructable, \
    MetricFunctionRegistryConstructable, TrainerConstructable, EvaluatorConstructable, MappedLabelsIteratorConstructable, \
    FilteredLabelsIteratorConstructable, FeatureEncodedIteratorConstructable, CombinedDatasetIteratorConstructable, \
    DataCollatorConstructable, PredictionPostProcessingRegistryConstructable, TrainComponentConstructable, EvalComponentConstructable, \
    IteratorViewConstructable, OneHotEncodedTargetsIteratorConstructable, InMemoryDatasetIteratorConstructable
from ml_gym.error_handling.exception import InjectMappingNotFoundError
# from ml_gym.util.logger import LogLevel, ConsoleLogger


class Injector:

    def __init__(self, mapping: Dict[str, Any], raise_mapping_not_found: bool = False):
        self.mapping = mapping
        self.raise_mapping_not_found = raise_mapping_not_found

    def inject_pass(self, component_parameters: Dict) -> Dict[str, Any]:
        def inject(tree: Union[Dict, List]) -> Dict[str, Any]:
            if isinstance(tree, dict):
                for key, sub_tree in tree.items():
                    if key == "injectable":
                        if tree["injectable"]["id"] not in self.mapping:
                            if self.raise_mapping_not_found:
                                raise InjectMappingNotFoundError
                            else:
                                tree[key] = sub_tree
                        else:
                            tree = self.mapping[sub_tree["id"]]
                    else:
                        tree[key] = inject(sub_tree)
                return tree
            elif isinstance(tree, list):
                return [inject(sub_tree) for sub_tree in tree]
            else:
                return tree
        copied_dict = copy.deepcopy(component_parameters)
        injected = {key: inject(parameter) for key, parameter in copied_dict.items()}
        return injected


@dataclass
class ComponentRepresentation:
    """ Direct class representation of components in the config dictionary
    """
    name: str
    component_type_key: str
    variant_key: str
    config: Dict = field(default_factory=dict)
    requirements: Dict[str, "RequirementRepresentation"] = field(default_factory=dict)

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
    name: str
    component_name: str
    subscription: List[int]


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
            ComponentVariant("IN_MEMORY_DATASET_ITERATORS", "DEFAULT", InMemoryDatasetIteratorConstructable),
            ComponentVariant("FILTERED_LABELS_ITERATOR", "DEFAULT", FilteredLabelsIteratorConstructable),
            ComponentVariant("ONE_HOT_ENCODED_TARGETS_ITERATOR", "DEFAULT", OneHotEncodedTargetsIteratorConstructable),
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
        Thereby, defining the dependency relationship of components, e.g., trainer depends on model."

        Args:
            component_config (Dict): Raw config describing the components and their dependencies

        Returns:
            Dict[str, ComponentRepresentation]: [description]
        """
        def create_component_representation(component_config: Dict, component_name: str = None) -> ComponentRepresentation:
            requirements = {}
            if "requirements" in component_config:
                requirements = {}
                for requirement in component_config.pop("requirements"):
                    requirement_component_name = requirement["component_name"]
                    name = requirement["name"]
                    subscription = requirement.get("subscription")
                    req_rep = RequirementRepresentation(name=name, component_name=requirement_component_name, subscription=subscription)
                    requirements[name] = req_rep
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
            component_representations[component_representation.name] = component_representation
        return component_representations

    def build_components_from_config(self, component_config: Dict, names_of_components_to_construct: List[str]) -> Dict:
        """Builds the components and returns a mapping from component name to component.
        Note, that dependencies are always rebuilt and not reused!

        Args:
            component_config (Dict): Raw config describing the components and their dependencies

        Returns:
            Dict: Component dictionary (component name -> Component)
        """
        def build_component(component_name: str, component_representation_graph: Dict[str, ComponentRepresentation], components: Dict[str, Any]):
            component_representation = component_representation_graph[component_name]
            # build the requirements
            requirement_components = {name: build_component(requirement.component_name, component_representation_graph, {})
                                      for name, requirement in component_representation.requirements.items()}

            # collect the requirements
            requirements = {name: Requirement(requirement_components[name], requirement.subscription)
                            for name, requirement in component_representation.requirements.items()}
            # build the requested component
            component_variants_registry = self.component_factory_registry[component_representation.component_type_key]
            component = component_variants_registry.construct(
                component_representation.variant_key, component_representation.name, component_representation.config, requirements)
            return component

        # calculate the dependency graph of components
        component_representation_graph = self._calc_dependency_graph(component_config)
        # build each component
        components: Dict[str, Any] = {}  # maps
        components = {component_name: build_component(component_name, component_representation_graph, {})
                      for component_name, component_representation in component_representation_graph.items()
                      if component_name in names_of_components_to_construct}
        return components
