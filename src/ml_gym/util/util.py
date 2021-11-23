from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.models.nn.net import NNModel
import json
import os
import torch
from data_stack.dataset.iterator import DatasetIteratorIF
from typing import Dict, List, Type
from copy import deepcopy
from ml_gym.data_handling.dataset_loader import DatasetLoader
from ml_gym.gym.inference_component import InferenceComponent
from ml_gym.util.grid_search import GridSearch
from ml_gym.validation.validator_factory import ValidatorFactory
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.batching.batch import InferenceResultBatch, DatasetBatch
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent
from ml_gym.gym.post_processing import PredictPostProcessingIF
import tqdm
from ml_gym.gym.jobs import AbstractGymJob


class ExportedModel:
    def __init__(self, model: NNModel, post_processors: List[PredictPostProcessingIF], model_path: str = None):
        self.model = model
        self.post_processors = post_processors
        self.model_path = model_path

    def predict_tensor(self, sample_tensor: torch.Tensor, targets: torch.Tensor = None, tags: torch.Tensor = None, no_grad: bool = True):
        if no_grad:
            with torch.no_grad():
                forward_result = self.model.forward(sample_tensor)
        else:
            forward_result = self.model.forward(sample_tensor)
        result_batch = InferenceResultBatch(targets=targets, tags=tags, predictions=forward_result)
        result_batch = PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)
        return result_batch

    def predict_dataset_batch(self, batch: DatasetBatch, no_grad: bool = True) -> InferenceResultBatch:
        if no_grad:
            with torch.no_grad():
                forward_result = self.model.forward(batch.samples)
        else:
            forward_result = self.model.forward(batch.samples)

        result_batch = InferenceResultBatch(targets=deepcopy(batch.targets), tags=deepcopy(batch.tags), predictions=forward_result)
        result_batch = PredictPostprocessingComponent.post_process(result_batch, post_processors=self.post_processors)
        return result_batch

    def predict_data_loader(self, dataset_loader: DatasetLoader, no_grad: bool = True) -> InferenceResultBatch:
        result_batches = [self.predict_dataset_batch(batch, no_grad) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)

    @staticmethod
    def from_model_and_preprocessors(model: NNModel, post_processors: List[PredictPostProcessingIF], model_path: str ) -> "ExportedModel":
        return ExportedModel(model, post_processors, model_path)


class ComponentLoader:

    @staticmethod
    def get_trained_exported_model(components: List, experiment_path: str, model_id: int,
                                   split_name: str, device: torch.device = None) -> ExportedModel:
        trained_model = ComponentLoader.get_trained_model(components, experiment_path, model_id, device)
        post_processors = components["eval_component"].post_processors[split_name]
        model_path = os.path.join(experiment_path, f"checkpoints/model_{model_id}.pt")
        exported_model = ExportedModel.from_model_and_preprocessors(trained_model, post_processors, model_path)
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
                                                   grid_search_id="bla",
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
        model = model.to(device)
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
