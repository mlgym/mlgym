from typing import Dict, List, Any
from ml_gym.blueprints.constructables import ModelRegistryConstructable
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.gym_jobs.standard_gym_job import AbstractGymJob, GymJobFactory
from ml_gym.batching.batch import DatasetBatch
from dataclasses import dataclass
from ml_gym.blueprints.component_factory import ComponentFactory, Injector
from ml_gym.data_handling.postprocessors.collator import Collator
from ml_gym.models.nn.net import NNModel
from torch import nn
import torch
import torch.nn.functional as F


class ConvNet(NNModel):

    def __init__(self, prediction_publication_key: str, layer_config: Dict, seed: int = 0):
        super().__init__(seed=seed)
        self.prediction_publication_key = prediction_publication_key
        self.conv_layers = nn.ModuleList([])
        self.fc_layers = nn.ModuleList([])
        for layer in layer_config:
            if layer["type"] == "conv":
                self.conv_layers.append(ConvNet.create_conv_layer_from_config(layer["params"]))
            elif layer["type"] == "fc":
                self.fc_layers.append(ConvNet.create_fc_layer_from_config(layer["params"]))

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
        output = self.conv_layers[0](output)
        output = F.relu(output)

        output = self.conv_layers[1](output)
        output = F.relu(output)
        output = F.max_pool2d(output, 2, 2)
        output = F.dropout(output, p=0.25, training=True)

        output = output.view(inputs.shape[0], -1)
        output = self.fc_layers[0](output)
        output = F.relu(output)
        output = F.dropout(output, p=0.5, training=True)
        output = self.fc_layers[1](output)

        return {self.prediction_publication_key: output}

    def forward(self, inputs: torch.Tensor) -> Dict[str, torch.Tensor]:
        return self.forward_impl(inputs)


@dataclass
class MNISTCollator(Collator):
    target_publication_key: str = None

    def __call__(self, batch: List[torch.Tensor]):
        """
        :param batch: batch format [no_samples, height, width, channels]
        :return:
        """
        # batch contains a list of tuples of structure (sequence, target)
        inputs = [item[0].to(self.device) for item in batch]
        inputs = torch.stack(inputs)
        # transform into vector
        # inputs = inputs.view(inputs.shape[0], -1)
        # transform into CHW matrix
        # inputs = inputs.permute(0, 3, 1, 2)
        inputs = inputs.reshape(-1, 1, 28, 28)
        targets_tensor = torch.tensor([item[1] for item in batch]).to(inputs[0].device)
        target_partitions = {self.target_publication_key: targets_tensor}
        return DatasetBatch(targets=target_partitions, tags=None, samples=inputs)


@dataclass
class MyModelRegistryConstructable(ModelRegistryConstructable):
    def _construct_impl(self):
        super()._construct_impl()
        self.model_registry.add_class("conv_net", ConvNet)
        return self.model_registry


class ConvNetBluePrint(BluePrint):
    def __init__(self, run_mode: AbstractGymJob.Mode, job_type: AbstractGymJob.Type, config: Dict, epochs: int,
                 dashify_logging_dir: str, grid_search_id: str,
                 run_id: str, external_injection: Dict[str, Any] = None):
        model_name = "conv_net"
        dataset_name = ""
        super().__init__(run_mode, job_type, model_name, dataset_name, epochs, config, dashify_logging_dir,
                         grid_search_id,
                         run_id, external_injection)

    @staticmethod
    def construct_components(config: Dict, component_names: List[str], device: torch.device,
                             external_injection: Dict[str, Any] = None) -> Dict[str, Any]:
        if external_injection is not None:
            injection_mapping = {"id_conv_mnist_standard_collator": MNISTCollator,
                                 "id_computation_device": device,
                                 **external_injection}
            injector = Injector(injection_mapping, raise_mapping_not_found=True)

        else:
            injection_mapping = {"id_conv_mnist_standard_collator": MNISTCollator}
            injector = Injector(injection_mapping, raise_mapping_not_found=False)

        component_factory = ComponentFactory(injector)
        component_factory.register_component_type("MODEL_REGISTRY", "DEFAULT", MyModelRegistryConstructable)

        components = component_factory.build_components_from_config(config, component_names)
        return components

    def construct(self, device: torch.device = None) -> 'AbstractGymJob':
        experiment_info = self.get_experiment_info()
        component_names = ["model", "trainer", "optimizer", "evaluator"]
        components = ConvNetBluePrint.construct_components(self.config, component_names, device,
                                                           self.external_injection)

        gym_job = GymJobFactory.get_gym_job(self.run_mode, job_type=self.job_type,
                                            experiment_info=experiment_info, epochs=self.epochs, **components)
        return gym_job
