from typing import Dict, List
import torch
from conv_net import ConvNet
from ml_gym.blueprints.constructables import ModelRegistryConstructable
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.jobs import AbstractGymJob, GymJob
from ml_gym.batch import DatasetBatch
from dataclasses import dataclass
from ml_gym.blueprints.component_factory import ComponentFactory, Injector
from ml_gym.data_handling.postprocessors.collator import CollatorIF


@dataclass
class MNISTCollator(CollatorIF):
    target_publication_key: str

    def __call__(self, batch: List[torch.Tensor]):
        """
        :param batch: batch format [no_samples, height, width, channels]
        :return:
        """
        # batch contains a list of tuples of structure (sequence, target)
        inputs = [item[0] for item in batch]
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
    def __init__(self, run_mode: AbstractGymJob.Mode, config: Dict, epochs: List[int], dashify_logging_dir: str, grid_search_id: str, run_id: str):
        model_name = "conv_net"
        dataset_name = ""
        super().__init__(model_name, dataset_name, epochs, config, dashify_logging_dir, grid_search_id, run_id)
        self.run_mode = run_mode

    def construct(self) -> 'AbstractGymJob':
        experiment_info = self.get_experiment_info(self.dashify_logging_dir, self.grid_search_id, self.model_name, self.dataset_name, self.run_id)
        component_names = ["model", "trainer", "optimizer", "evaluator"]

        injection_mapping = {"id_conv_mnist_standard_collator": MNISTCollator}
        injector = Injector(injection_mapping)
        component_factory = ComponentFactory(injector)
        component_factory.register_component_type("MODEL_REGISTRY", "DEFAULT", MyModelRegistryConstructable)
        components = component_factory.build_components_from_config(self.config, component_names)
        gym_job = GymJob(self.run_mode, experiment_info=experiment_info, epochs=self.epochs, **components)
        return gym_job
