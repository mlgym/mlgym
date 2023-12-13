import torch
from ml_gym.modes import RunMode
from dataclasses import dataclass
from ResNet34Model import ResNet34
from typing import Dict, List, Any
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.error_handling.exception import DatasetNotFoundError
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from ml_gym.blueprints.component_factory import ComponentFactory, Injector
from ml_gym.blueprints.constructables import ComponentConstructable, ModelRegistryConstructable

@dataclass
class Cifar10DatasetConstructable(ComponentConstructable):
    dataset_identifier: str = ""
    dataset_folder_path: str = None

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_dict = {}
        if self.dataset_folder_path is None:
            raise DatasetNotFoundError("Dataset path not specified")
        # What Next????
        
@dataclass
class MyModelRegistryConstructable(ModelRegistryConstructable):
    def _construct_impl(self):
        super()._construct_impl()
        self.model_registry.add_class("resnet34", ResNet34)
        return self.model_registry
    
class ResNet34BluePrint(BluePrint):

    def __init__(self, run_mode: RunMode, config: Dict[str, Any], grid_search_id: str,
                 experiment_id: str, external_injection: Dict[str, Any] = None,
                 warm_start_epoch: int = 0):
        super().__init__(run_mode, config, grid_search_id, experiment_id, external_injection, warm_start_epoch)
        
    @staticmethod
    def construct_components(config: Dict, component_names: List[str], device: torch.device,
                             external_injection: Dict[str, Any] = None) -> Dict[str, Any]:
        if external_injection is not None:
            injection_mapping = {"id_resnet34_collator": None,
                                 "id_computation_device": device,
                                 **external_injection}
            injector = Injector(injection_mapping, raise_mapping_not_found=True)

        else:
            injection_mapping = {"id_resnet34_collator": None}
            injector = Injector(injection_mapping, raise_mapping_not_found=False)

        component_factory = ComponentFactory(injector)
        component_factory.register_component_type("MODEL_REGISTRY", "DEFAULT", MyModelRegistryConstructable)
        component_factory.register_component_type("DATASET_ITERATORS", "Cifar10DatasetConstructable", Cifar10DatasetConstructable)

        components = component_factory.build_components_from_config(config, component_names)
        return components
    
    def construct(self, device: torch.device = None) -> Dict[str, Any]:
        component_names = ["model", "trainer", "optimizer", "evaluator", "early_stopping_strategy", "checkpointing_strategy", "lr_scheduler"]
        components = ResNet34BluePrint.construct_components(self.config, component_names, device, self.external_injection)

        return components
    