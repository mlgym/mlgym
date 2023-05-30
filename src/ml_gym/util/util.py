from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.models.nn.net import NNModel
import json
import os
import torch
from data_stack.dataset.iterator import DatasetIteratorIF
from typing import Dict, List, Type, Callable
from copy import deepcopy
from ml_gym.data_handling.dataset_loader import DatasetLoader, DatasetLoaderFactory
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.util.grid_search import GridSearch
from ml_gym.validation.validator_factory import ValidatorFactory
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF
import tqdm
from ml_gym.gym.gym_jobs.standard_gym_job import AbstractGymJob
from ml_gym.error_handling.exception import SystemInfoFetchError
from data_stack.dataset.iterator import InformedDatasetIteratorIF
import platform
import torch
import psutil
import pkg_resources


class SystemEnv:
    @staticmethod
    def create_system_info() -> Dict:
        """
        Fetch System Information for model card.

        :returns: Dict- System Information of host machine (CPU & GPU)
        """
        try:
            info = {}
            info["system_info"] = platform.platform()
            info["architecture"] = platform.architecture()
            info["machine_type"] = platform.machine()
            info["processor"] = platform.processor()
            info["num_processor_cores"] = psutil.cpu_count()
            info["ram"] = str(round(psutil.virtual_memory().total / (1024.0**3))) + " GB"
            info["python-version"] = platform.python_version()
            info["python-packages"] = [{"name":p.project_name, "version": p.version} for p in pkg_resources.working_set]
            if torch.cuda.is_available():
                info["CUDNN_version"] = torch.backends.cudnn.version()
                info["num_cuda_device"] = torch.cuda.device_count()
                dev_list = []
                for i in range(torch.cuda.device_count()):
                    dev_list.append(
                        {
                            "name": torch.cuda.get_device_name(i),
                            "total_memory": f"{round(torch.cuda.get_device_properties(i).total_memory /(1024.0**3), 2)} GB",
                            "memory_allocated": f"{round(torch.cuda.memory_allocated(i) /(1024.0**3), 2)} GB",
                            "memory_reserved": f"{round(torch.cuda.memory_reserved(i) /(1024.0**3), 2)} GB",
                            "max_memory_reserved": f"{round(torch.cuda.max_memory_reserved(i) /(1024.0**3), 2)} GB",
                        }
                    )
                info["cuda_device_list"] = dev_list
            return info
        except Exception as e:
            raise SystemInfoFetchError(f"Unable to fetch System Info") from e

class ExportedModel:
    def __init__(self, model: NNModel, post_processors: List[PredictPostProcessingIF], model_path: str = None, device: torch.device = None):
        self.model = model
        self.post_processors = post_processors
        self.model_path = model_path
        self._device = device if device is not None else torch.device("cpu")
        self.model.to(self._device)

    @property
    def device(self) -> torch.device:
        return self._device

    @device.setter
    def device(self, d: torch.device):
        self._device = d
        self.model.to(self._device)

    def predict_tensor(self, sample_tensor: torch.Tensor, targets: torch.Tensor = None, tags: torch.Tensor = None, no_grad: bool = True):
        sample_tensor = sample_tensor.to(self._device)
        if no_grad:
            with torch.no_grad():
                forward_result = self.model.forward(sample_tensor)
        else:
            forward_result = self.model.forward(sample_tensor)
        result_batch = InferenceResultBatch(targets=targets, tags=tags, predictions=forward_result)
        result_batch = PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)
        return result_batch

    def predict_dataset_batch(self, batch: DatasetBatch, no_grad: bool = True) -> InferenceResultBatch:
        batch.to(self._device)
        if no_grad:
            with torch.no_grad():
                forward_result = self.model.forward(batch.samples)
        else:
            forward_result = self.model.forward(batch.samples)

        result_batch = InferenceResultBatch(targets=deepcopy(batch.targets), tags=deepcopy(batch.tags), predictions=forward_result)
        result_batch = PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)
        result_batch.to_cpu()
        return result_batch

    def predict_dataset_iterator(self, dataset_iterator: InformedDatasetIteratorIF,
                                 batch_size: int, collate_fn: Callable, no_grad: bool = True) -> InferenceResultBatch:
        split_key = "dataset_split"
        sampling_strategies = {split_key: {"strategy": "IN_ORDER"}}
        dataset_loader = DatasetLoaderFactory.get_splitted_data_loaders({split_key: dataset_iterator}, batch_size=batch_size,
                                                                        sampling_strategies=sampling_strategies,
                                                                        collate_fn=collate_fn)[split_key]
        irb = self.predict_data_loader(dataset_loader=dataset_loader, no_grad=no_grad)
        return irb

    def predict_data_loader(self, dataset_loader: DatasetLoader, no_grad: bool = True) -> InferenceResultBatch:
        dataset_loader.device = self._device
        result_batches = [self.predict_dataset_batch(batch, no_grad) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)

    @staticmethod
    def from_model_and_preprocessors(model: NNModel, post_processors: List[PredictPostProcessingIF], model_path: str,
                                     device: torch.device = None) -> "ExportedModel":
        return ExportedModel(model, post_processors, model_path, device=device)


class ComponentLoader:

    @staticmethod
    def get_trained_exported_model(components: List, experiment_path: str, model_id: int,
                                   split_name: str, device: torch.device = None) -> ExportedModel:
        trained_model = ComponentLoader.get_trained_model(components, experiment_path, model_id, device)
        post_processors = components["eval_component"].post_processors[split_name]
        model_path = os.path.join(experiment_path, f"checkpoints/model_{model_id}.pt")
        exported_model = ExportedModel.from_model_and_preprocessors(trained_model, post_processors, model_path, device)
        return exported_model

    @staticmethod
    def get_components(experiment_path: str, blueprint_type: Type[BluePrint], component_names: List[str]):
        config_path = os.path.join(experiment_path, "config.json")

        with open(config_path, "r") as fd:
            config = json.load(fd)
        components = blueprint_type.construct_components(config=config, component_names=component_names)
        return components

    @staticmethod
    def get_components_from_grid_search(gs_path: str, blueprint_type: Type[BluePrint], component_names: List[str], gs_id: int = 0):
        run_id_to_config_dict = {str(run_id): config for run_id, config in enumerate(GridSearch.create_gs_configs_from_path(gs_path))}
        experiment_config = run_id_to_config_dict[f"{gs_id}"]
        components = blueprint_type.construct_components(config=experiment_config, component_names=component_names)
        return components

    @staticmethod
    def get_components_from_nested_cv(gs_path: str, cv_path: str, blueprint_type: Type[BluePrint], component_names: List[str]):
        gs_config = YAMLConfigLoader.load(gs_path)
        cv_config = YAMLConfigLoader.load(cv_path)
        nested_cv = ValidatorFactory.get_nested_cv(gs_config=gs_config,
                                                   cv_config=cv_config,
                                                   blue_print_type=blueprint_type)
        blue_print = nested_cv.create_blue_prints(blueprint_type, AbstractGymJob.Type.STANDARD, gs_config, 1, dashify_logging_path="")[0]
        components = blueprint_type.construct_components(
            config=blue_print.config, component_names=component_names, external_injection=blue_print.external_injection)
        return components

    @staticmethod
    def get_trained_model(components: List, experiment_path: str, model_id: int, device: torch.device = None) -> NNModel:
        model_state_dict_path = os.path.join(experiment_path, f"checkpoints/model_{model_id}.pt")
        model = deepcopy(components["model"])
        # load model
        model_state = torch.load(model_state_dict_path, map_location=device)
        model.load_state_dict(model_state)
        return model

    @staticmethod
    def get_datasets(components: List) -> Dict[str, DatasetIteratorIF]:
        dataset_keys = list(
            components["evaluator"].eval_component.dataset_loaders.keys())
        datasets_dict = {
            key: components["evaluator"].eval_component.dataset_loaders[key].dataset for key in dataset_keys}
        return datasets_dict

    @staticmethod
    def get_dataloaders(components: List) -> Dict[str, DatasetLoader]:
        return components["evaluator"].eval_component.dataset_loaders

    @staticmethod
    def get_inference_component(components: List) -> InferenceComponent:
        return components["evaluator"].eval_component.inference_component
