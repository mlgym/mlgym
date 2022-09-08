from typing import Dict, List, Any
from ml_gym.modes import RunMode
from ml_gym.persistency.logging import ExperimentStatusLogger, MLgymStatusLoggerCollectionConstructable
import torch
from ml_gym.blueprints.constructables import ModelRegistryConstructable
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.gym.jobs import AbstractGymJob, GymJobFactory
from ml_gym.batching.batch import DatasetBatch
from dataclasses import dataclass
from ml_gym.blueprints.component_factory import ComponentFactory, Injector
from ml_gym.data_handling.postprocessors.collator import Collator

from conv_net import ConvNet


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
    def __init__(self, run_mode: RunMode, config: Dict, epochs: int, grid_search_id: str,
                 experiment_id: str, external_injection: Dict[str, Any] = None,
                 logger_collection_constructable: MLgymStatusLoggerCollectionConstructable = None):
        super().__init__(run_mode, epochs, config, grid_search_id,
                         experiment_id, external_injection, logger_collection_constructable)

    @staticmethod
    def construct_components(config: Dict, component_names: List[str], device: torch.device, external_injection: Dict[str, Any] = None) -> Dict[str, Any]:
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

    def construct(self, device: torch.device = None) -> AbstractGymJob:
        component_names = ["model", "trainer", "optimizer", "evaluator", "early_stopping_strategy"]
        components = ConvNetBluePrint.construct_components(self.config, component_names, device, self.external_injection)

        logger_collection = self.logger_collection_constructable.construct()
        experiment_status_logger = ExperimentStatusLogger(logger=logger_collection, grid_search_id=self.grid_search_id,
                                                          experiment_id=self.experiment_id)

        gym_job = GymJobFactory.get_gym_job(self.run_mode,
                                            epochs=self.epochs,
                                            experiment_status_logger=experiment_status_logger,
                                            **components)
        return gym_job
