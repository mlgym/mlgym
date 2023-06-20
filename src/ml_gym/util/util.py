from datetime import datetime
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
from ml_gym.error_handling.exception import ModelCardCreationError, SystemInfoFetchError, ModelDetailsCreationError, TrainingDetailsCreationError, EvalDetailsCreationError, DatasetDetailsCreationError
from data_stack.dataset.iterator import InformedDatasetIteratorIF
import platform
import torch
import psutil
import pkg_resources
from dataclasses import dataclass

@dataclass
class ModelDetails:
    model_description: str = ""
    model_version: str = "" 
    grid_search_id: str = ""
    train_date: str = ""
    source_repo: str = ""
    train_params: int = 0

    def toJSON(self) -> Dict:
        model_card ={}
        model_card["model_description"] = self.model_description
        model_card["model_version"] = self.model_version
        model_card["grid_search_id"] = self.grid_search_id
        model_card["train_date"] = self.train_date
        model_card["source_repo"] = self.source_repo
        model_card["train_params"] = self.train_params
        return model_card

@dataclass
class DatasetDetails:
    dataset_splits: dict = None
    considered_dataset: str = ""
    label_distribution: str = ""

    def toJSON(self) -> Dict:
        model_card ={}
        model_card["dataset_splits"] = self.dataset_splits
        model_card["considered_dataset"] = self.considered_dataset
        model_card["label_distribution"] = self.label_distribution
        return model_card

@dataclass
class ExperimentEnvironment:
    system_env: dict = None
    carbon_footprint: dict = None
    entry_point_cmd: str = ""

    def toJSON(self) -> Dict:
        model_card ={}
        model_card["system_env"] = self.system_env
        model_card["carbon_footprint"] = self.carbon_footprint
        model_card["entry_point_cmd"] = self.entry_point_cmd
        return model_card

    def create_system_info() -> Dict:
        """
        Fetch System Information for model card.

        :returns: 
            info (Dict): System Information of host machine (CPU & GPU)
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
            info["python-packages"] = [{"name": p.project_name, "version": p.version} for p in pkg_resources.working_set]
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

@dataclass
class TrainingDetails:
    hyperparams: dict = None
    loss_func: str = ""
    optimizer: str = ""

    def toJSON(self) -> Dict:
        model_card ={}
        model_card["hyperparams"] = self.hyperparams
        model_card["loss_func"] = self.loss_func
        model_card["optimizer"] = self.optimizer
        return model_card

@dataclass
class EvalDetails:
    loss_funcs: list = None
    metrics: list = None

    def toJSON(self) -> Dict:
        model_card ={}
        model_card["loss_funcs"] = self.loss_funcs
        model_card["metrics"] = self.metrics
        return model_card

@dataclass
class ModelCard:
    model_details: ModelDetails
    dataset_details: DatasetDetails
    experiment_environment: ExperimentEnvironment
    training_details: TrainingDetails
    eval_details: EvalDetails

    def toJSON(self) -> Dict:
        model_card = {}
        model_card["model_details"] = self.model_details.toJSON()
        model_card["dataset_details"] = self.dataset_details.toJSON()
        model_card["training_details"] = self.training_details.toJSON()
        model_card["eval_details"] = self.eval_details.toJSON()
        model_card["experiment_environment"] = self.experiment_environment.toJSON()
        return model_card

class ModelCardFactory:

    @staticmethod
    def create_model_card(grid_search_id: str, exp_config: dict, gs_config: dict, model = None) -> Dict:
        """
        Create Model card.
        :params:
                grid_search_id (str): Grid Search ID created for the run.
                exp_config (dict): Experiment configuration.
                gs_config (dict): Grid Search configuration.
        :returns:
                model_card (ModelCard): Model card object to be converted into json file.
        """
        
        def update_model_details(grid_search_id: str, gs_config: dict, model) -> ModelDetails:
            """
            Function to initialize ModelDetails object.
            :params:
                    grid_search_id (str): Grid Search ID created for the run.
                    gs_config (dict): Grid Search configuration.
            :returns:
                    obj (ModelDetails): initialized model details object.
            """
            try:
                if model is not None:
                    pytorch_total_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
                else:
                    pytorch_total_params = 0
                train_date = datetime.now().strftime("%d-%m-%Y")
                model_info = gs_config["model_info"]
                return ModelDetails(model_description = model_info["model_description"], model_version = model_info["model_version"], grid_search_id = grid_search_id, train_date = train_date, source_repo = model_info["source_repo"], train_params= pytorch_total_params)
            except Exception as e:
                raise ModelDetailsCreationError(f"Error while fetching Model Details for Model card") from e
        
        def update_dataset_details(exp_config: dict) -> DatasetDetails:
            """
            Function to initialize DatasetDetails object.
            :params:
                    exp_config (dict): Experiment configuration.
            :returns:
                    obj (DatasetDetails): initialized dataset details object.
            """
            try:
                dataset_splits = {"split_config": exp_config["dataset_iterators"]["config"]["split_configs"], 
                              "splits_percentage": exp_config["splitted_dataset_iterators"]["config"]["split_configs"]}
            
                return DatasetDetails(considered_dataset = exp_config["dataset_iterators"]["config"]["dataset_identifier"], dataset_splits = dataset_splits)
            except Exception as e:
                raise DatasetDetailsCreationError(f"Error while fetching Dataset Details for Model card.") from e
        
        def update_training_details(exp_config: dict, gs_config: dict) -> TrainingDetails:
            """
            Function to initialize TrainingDetails object.
            :params:
                    exp_config (dict): Experiment configuration.
            :returns:
                    obj (TrainingDetails): initialized training details object.
            """
            try:
                hyperparams = {}
                hyperparams["optimizer"] = exp_config["optimizer"]["config"]["params"]
                return TrainingDetails( hyperparams = hyperparams, loss_func = exp_config["train_component"]["config"]["loss_fun_config"]["tag"], optimizer = exp_config["optimizer"]["config"]["optimizer_key"])
            except Exception as e:
                raise TrainingDetailsCreationError(f"Error while fetching Training Details for Model card.") from e
        
        def update_evaluation_details(exp_config: dict) -> EvalDetails:
            """
            Function to initialize EvalDetails object.
            :params:
                    exp_config (dict): Experiment configuration.
            :returns:
                    obj (EvalDetails): initialized evaluation details object.
            """
            loss_funcs = []
            metrics = []
            try:
                for loss_func_config in exp_config["eval_component"]["config"]["loss_funs_config"]:
                    loss_funcs.append(loss_func_config["tag"])
            
                for metric_config in exp_config["eval_component"]["config"]["metrics_config"]:
                    metrics.append({"name": metric_config["tag"], "params": metric_config["params"]})

                return EvalDetails(loss_funcs = loss_funcs, metrics = metrics)
            except Exception as e:
                raise EvalDetails(f"Error while fetching Eval Details for Model card.") from e

        try:
            experiment_env = ExperimentEnvironment(system_env = ExperimentEnvironment.create_system_info())
            model_details = update_model_details(grid_search_id = grid_search_id, gs_config = gs_config, model=model)
            dataset_details = update_dataset_details(exp_config = exp_config)
            training_details = update_training_details(exp_config = exp_config, gs_config = gs_config)
            eval_details = update_evaluation_details(exp_config = exp_config)
            model_card = ModelCard(
                model_details = model_details,
                dataset_details = dataset_details,
                experiment_environment = experiment_env,
                training_details = training_details,
                eval_details =eval_details
            )
            return model_card.toJSON()
        except Exception as e:
            raise ModelCardCreationError(f"Unable to create Model Card") from e

class ExportedModel:
    """
    ExportedModel Class cpontains functions to export model components.
    """
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
        """
        Get predictions perfomed on the model.
        :params:
                sample_tensor (torch.Tensor): Sample Data.
                targets (torch.Tensor): Target Data.
                tags (torch.Tensor): Tags for Data.
                no_grad (bool): Whether to return predictions in inference mode.
        
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the model.
        """
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
        """
        Get predictions perfomed on the batch of dataset.
        :params:
                batch (DatasetBatch): A batch of samples and its targets and tags.
                no_grad (bool): Whether to return predictions in inference mode.
        
        :returns:
            result_batch (InferenceResultBatch): Prediction performed on the batch of dataset.
        """
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
        """
        Get predictions perfomed on the Dataset iterators.
        :params:
                dataset_iterator (InformedDatasetIteratorIF): Dataset Iterator Interface object.
                batch_size (int): Batch size.
                collate_fn (Callable): Collate function.
                no_grad (bool): Whether to return predictions in inference mode.
        
        :returns:
            irb (InferenceResultBatch): Prediction performed on Dataset iterators.
        """
        split_key = "dataset_split"
        sampling_strategies = {split_key: {"strategy": "IN_ORDER"}}
        dataset_loader = DatasetLoaderFactory.get_splitted_data_loaders({split_key: dataset_iterator}, batch_size=batch_size,
                                                                        sampling_strategies=sampling_strategies,
                                                                        collate_fn=collate_fn)[split_key]
        irb = self.predict_data_loader(dataset_loader=dataset_loader, no_grad=no_grad)
        return irb

    def predict_data_loader(self, dataset_loader: DatasetLoader, no_grad: bool = True) -> InferenceResultBatch:
        """
        Get predictions perfomed on the Dataset iterators.
        :params:
                dataset_loader (DatasetLoader): Obhect of DatasetLoader used to load Data to be trained on.
                no_grad (bool): Whether to return predictions in inference mode.
        
        :returns:
            InferenceResultBatch object: Has combined results from batches.
        """
        dataset_loader.device = self._device
        result_batches = [self.predict_dataset_batch(batch, no_grad) for batch in tqdm.tqdm(dataset_loader, desc="Batches processed:")]
        return InferenceResultBatch.combine(result_batches)

    @staticmethod
    def from_model_and_preprocessors(model: NNModel, post_processors: List[PredictPostProcessingIF], model_path: str,
                                     device: torch.device = None) -> "ExportedModel":
        """
        Get ExportedModel object.
        :params:
                model (NNModel): Torch Neural Network module.
                post_processors (List[PredictPostProcessingIF]): List of Post Processors.
                model_path (str): Path to save exported model.
                device (torch.device): Torch device.
        
        :returns:
            ExportedModel object.
        """
        return ExportedModel(model, post_processors, model_path, device=device)


class ComponentLoader:
    """
    ComponentLoader contains functions to load compomnents from exported model.
    """

    @staticmethod
    def get_trained_exported_model(components: List, experiment_path: str, model_id: int,
                                   split_name: str, device: torch.device = None) -> ExportedModel:
        """
        Get Trained Exported model.
        :params:
                components (List): List of components to be fetched.
                experiment_path (str): Path to experiment.
                model_id (int): Model id.
                split_name (str): Split name.
                device (torch.device): Torch device.
        
        :returns:
            exported_model (ExportedModel): ExportedModel object.
        """
        trained_model = ComponentLoader.get_trained_model(components, experiment_path, model_id, device)
        post_processors = components["eval_component"].post_processors[split_name]
        model_path = os.path.join(experiment_path, f"checkpoints/model_{model_id}.pt")
        exported_model = ExportedModel.from_model_and_preprocessors(trained_model, post_processors, model_path, device)
        return exported_model

    @staticmethod
    def get_components(experiment_path: str, blueprint_type: Type[BluePrint], component_names: List[str]):
        """
        Get components from the trained model.
        :params:
                experiment_path (str): Path to experiment.
                blueprint_type (Type[BluePrint]): BluePrint type.
                component_names (List[str]): List of component names.
        
        :returns:
            components (list[Any]): List of components constructed based on the blueprint_type.
        """
        config_path = os.path.join(experiment_path, "config.json")

        with open(config_path, "r") as fd:
            config = json.load(fd)
        components = blueprint_type.construct_components(config=config, component_names=component_names)
        return components

    @staticmethod
    def get_components_from_grid_search(gs_path: str, blueprint_type: Type[BluePrint], component_names: List[str], gs_id: int = 0):
        """
        Get components from Grid Search.
        :params:
                gs_path (str): path to gs config file.
                blueprint_type (Type[BluePrint]): BluePrint type.
                component_names (List[str]): List of component names.
                gs_id (int): Grid Search id.
        
        :returns:
            components (list[Any]): List of components constructed based on the blueprint_type.
        """
        run_id_to_config_dict = {str(run_id): config for run_id, config in enumerate(GridSearch.create_gs_configs_from_path(gs_path))}
        experiment_config = run_id_to_config_dict[f"{gs_id}"]
        components = blueprint_type.construct_components(config=experiment_config, component_names=component_names)
        return components

    @staticmethod
    def get_components_from_nested_cv(gs_path: str, cv_path: str, blueprint_type: Type[BluePrint], component_names: List[str]):
        """
        Get components from Nested CV.
        :params:
                gs_path (str): path to gs config file.
                cv_path (str): path to cv config file.
                blueprint_type (Type[BluePrint]): BluePrint type.
                component_names (List[str]): List of component names.
        
        :returns:
            components (list[Any]): List of components constructed based on the blueprint_type.
        """
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
        """
        Get Trained model.
        :params:
                components (List): List of components to be used.
                experiment_path (str): path to experiment dir.
                model_id (int): Model id.
                device (torch.device): Device to be used.
        
        :returns:
            model (NNModel): Torch Neural Network module.
        """
        model_state_dict_path = os.path.join(experiment_path, f"checkpoints/model_{model_id}.pt")
        model = deepcopy(components["model"])
        # load model
        model_state = torch.load(model_state_dict_path, map_location=device)
        model.load_state_dict(model_state)
        return model

    @staticmethod
    def get_datasets(components: List) -> Dict[str, DatasetIteratorIF]:
        """
        Get Datasets.
        :params:
            components (List): List of components to be used.
        :returns:
            datasets_dict (Dict[str, DatasetIteratorIF]): Dict of datasets.
        """
        dataset_keys = list(
            components["evaluator"].eval_component.dataset_loaders.keys())
        datasets_dict = {
            key: components["evaluator"].eval_component.dataset_loaders[key].dataset for key in dataset_keys}
        return datasets_dict

    @staticmethod
    def get_dataloaders(components: List) -> Dict[str, DatasetLoader]:
        """
        Get DataLoaders.
        :params:
            components (List): List of components to be used.
        :returns:
            dataloaders_dict (Dict[str, DatasetLoader]): Dict of DataLoaders.
        """
        return components["evaluator"].eval_component.dataset_loaders

    @staticmethod
    def get_inference_component(components: List) -> InferenceComponent:
        """
        Get InferenceComponent.
        :params:
            components (List): List of components to be used.
        :returns:
            inference_component (InferenceComponent): InferenceComponent.
        """
        return components["evaluator"].eval_component.inference_component
