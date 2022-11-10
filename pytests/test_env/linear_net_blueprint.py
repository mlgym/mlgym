import os
from typing import List, Any, Tuple
from data_stack.dataset.factory import BaseDatasetFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF, SequenceDatasetIterator, \
    DatasetIteratorIF
from data_stack.dataset.meta import MetaFactory, IteratorMeta
from data_stack.repository.repository import DatasetRepository
from ml_gym.blueprints.constructables import ModelRegistryConstructable, ComponentConstructable
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.data_handling.postprocessors.factory import ModelGymInformedIteratorFactory
from ml_gym.gym.jobs import AbstractGymJob, GymJobFactory
from ml_gym.batching.batch import DatasetBatch
from dataclasses import dataclass, field
from ml_gym.blueprints.component_factory import ComponentFactory, Injector
from ml_gym.data_handling.postprocessors.collator import Collator

from ml_gym.models.nn.net import NNModel
from typing import Dict
from torch import nn
import torch
import torch.nn.functional as F
from ml_gym.modes import RunMode

os.environ['CUDA_LAUNCH_BLOCKING'] = '1'


class LinearNet(NNModel):

    def __init__(self, prediction_publication_key: str, layer_config: Dict, seed: int = 0):
        super().__init__(seed=seed)
        self.prediction_publication_key = prediction_publication_key
        self.conv_layers = nn.ModuleList([])
        self.fc_layers = nn.ModuleList([])
        for layer in layer_config:
            if layer["type"] == "conv":
                self.conv_layers.append(LinearNet.create_conv_layer_from_config(layer["params"]))
            elif layer["type"] == "fc":
                self.fc_layers.append(LinearNet.create_fc_layer_from_config(layer["params"]))

    @staticmethod
    def create_conv_layer_from_config(layer_dict) -> nn.Module:
        return nn.Conv2d(in_channels=layer_dict["in_channels"],
                         out_channels=layer_dict["out_channels"],
                         kernel_size=layer_dict["kernel_size"],
                         stride=layer_dict["stride"])

    @staticmethod
    def create_fc_layer_from_config(layer_dict) -> nn.Module:
        return nn.Linear(in_features=layer_dict["in_features"],
                         out_features=layer_dict["out_features"])

    def forward_impl(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        output = inputs
        output = self.fc_layers[0](output)
        output = F.relu(output)
        output = F.dropout(output, p=0.5, training=True)
        output = self.fc_layers[1](output)

        return {self.prediction_publication_key: output}

    def forward(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        return self.forward_impl(inputs)


@dataclass
class MockedDataCollator(Collator):
    target_publication_key: str = None

    def __call__(self, batch: List[torch.Tensor]):
        """
        :param batch: batch format [no_samples, height, width, channels]
        :return:
        """
        # batch contains a list of tuples of structure (sequence, target)
        inputs = [item[0].to(self.device) for item in batch]
        inputs = torch.stack(inputs)
        inputs = inputs.reshape(-1, 1)
        targets_tensor = torch.tensor([item[1] for item in batch]).reshape(-1, 1).to(inputs[0].device)
        target_partitions = {self.target_publication_key: targets_tensor}
        return DatasetBatch(targets=target_partitions, tags=None, samples=inputs)


@dataclass
class MyModelRegistryConstructable(ModelRegistryConstructable):
    def _construct_impl(self):
        super()._construct_impl()
        self.model_registry.add_class("linear_net", LinearNet)
        return self.model_registry


@dataclass
class MockedDatasetFactory(BaseDatasetFactory):
    def __init__(self):
        super().__init__()
        samples = [1] * 100 + [2] * 200 + [3] * 300
        targets = [1] * 100 + [2] * 200 + [3] * 300

        test_samples = [1] * 20 + [2] * 40 + [3] * 60
        test_targets = [1] * 20 + [2] * 40 + [3] * 60

        samples = torch.Tensor(samples)
        targets = torch.Tensor(targets)
        test_samples = torch.Tensor(test_samples)
        test_targets = torch.Tensor(test_targets)

        self.resource_definitions = {
            "train": [
                samples,
                targets
            ],
            "test": [
                test_samples,
                test_targets
            ]
        }

    def _get_iterator(self, split: str) -> DatasetIteratorIF:
        sample_resource = self.resource_definitions[split][0]
        target_resource = self.resource_definitions[split][1].unsqueeze(1)
        return SequenceDatasetIterator([sample_resource, target_resource])

    def get_dataset_iterator(self, config: Dict[str, Any] = None) -> Tuple[DatasetIteratorIF, IteratorMeta]:
        dataset_iterator = self._get_iterator(**config)
        return dataset_iterator, IteratorMeta(sample_pos=0, target_pos=1, tag_pos=2)


@dataclass
class MyDatasetRepositoryConstructable(ComponentConstructable):
    def _construct_impl(self) -> DatasetRepository:
        dataset_repository: DatasetRepository = DatasetRepository()
        dataset_repository.register("mocked_dataset", MockedDatasetFactory())

        return dataset_repository


@dataclass
class MyDatasetIteratorConstructable(ComponentConstructable):
    dataset_identifier: str = ""
    split_configs: Dict[str, Any] = field(default_factory=dict)

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        dataset_dict = {}
        for split_config in self.split_configs:
            dataset_repository = self.get_requirement("repository")
            split_name = split_config["split"]
            iterator, iterator_meta = dataset_repository.get(self.dataset_identifier, split_config)
            dataset_meta = MetaFactory.get_dataset_meta(identifier=self.component_identifier,
                                                        dataset_name=self.dataset_identifier,
                                                        dataset_tag=split_name,
                                                        iterator_meta=iterator_meta)
            dataset_dict[split_name] = ModelGymInformedIteratorFactory.get_dataset_iterator(iterator, dataset_meta)
        return dataset_dict


class LinearBluePrint(BluePrint):
    def __init__(self, run_mode: RunMode, config: Dict, epochs: int,
                 dashify_logging_dir: str, grid_search_id: str,
                 run_id: str, external_injection: Dict[str, Any] = None):
        model_name = "linear_net"
        dataset_name = ""
        super().__init__(run_mode, model_name, dataset_name, epochs, config, dashify_logging_dir,
                         grid_search_id,
                         run_id, external_injection)

    @staticmethod
    def construct_components(config: Dict, component_names: List[str], device: torch.device = None,
                             external_injection: Dict[str, Any] = None) -> Dict[str, Any]:
        if external_injection is not None:
            injection_mapping = {"id_conv_mnist_standard_collator": MockedDataCollator,
                                 "id_computation_device": device,
                                 **external_injection}
            injector = Injector(injection_mapping, raise_mapping_not_found=True)

        else:
            injection_mapping = {"id_conv_mnist_standard_collator": MockedDataCollator}
            injector = Injector(injection_mapping, raise_mapping_not_found=False)

        component_factory = ComponentFactory(injector)

        component_factory.register_component_type("MODEL_REGISTRY", "DEFAULT", MyModelRegistryConstructable)
        component_factory.register_component_type("DATASET_REPOSITORY", "DEFAULT", MyDatasetRepositoryConstructable)
        component_factory.register_component_type("DATASET_ITERATORS", "DEFAULT", MyDatasetIteratorConstructable)

        components = component_factory.build_components_from_config(config, component_names)
        return components

    def construct(self, device: torch.device = None) -> 'AbstractGymJob':
        experiment_info = self.get_experiment_info()
        component_names = ["model", "trainer", "optimizer", "evaluator"]
        components = LinearBluePrint.construct_components(self.config, component_names, device,
                                                          self.external_injection)

        gym_job = GymJobFactory.get_gym_job(self.run_mode,
                                            experiment_info=experiment_info, epochs=self.epochs, **components)
        return gym_job
