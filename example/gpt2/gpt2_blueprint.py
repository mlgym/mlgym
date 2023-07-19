from ml_gym.error_handling.exception import DatasetNotFoundError
from typing import Dict, List, Any
from ml_gym.data_handling.postprocessors.factory import ModelGymInformedIteratorFactory
from ml_gym.modes import RunMode
import torch
from ml_gym.blueprints.constructables import ComponentConstructable, ModelRegistryConstructable
from ml_gym.blueprints.blue_prints import BluePrint
from ml_gym.batching.batch import DatasetBatch
from dataclasses import dataclass
from ml_gym.blueprints.component_factory import ComponentFactory, Injector
from ml_gym.data_handling.postprocessors.collator import Collator
from gpt2_model import GPT2LLM
from transformers import DataCollatorForLanguageModeling, GPT2TokenizerFast
from data_stack.dataset.meta import MetaFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from datasets import load_from_disk
from clm_loss_function import LMLossFunctionRegistryConstructable


@dataclass
class LMWikiBookCorpusDatasetConstructable(ComponentConstructable):
    dataset_identifier: str = ""
    dataset_folder_path: str = None

    def _construct_impl(self) -> Dict[str, InformedDatasetIteratorIF]:
        if self.dataset_folder_path is None:
            raise DatasetNotFoundError("Dataset path not specified")
        wiki_dataset = load_from_disk(self.dataset_folder_path)
        split_name = "train"
        iterator_meta = MetaFactory.get_iterator_meta(sample_pos=0, target_pos=1, tag_pos=0)
        dataset_meta = MetaFactory.get_dataset_meta(identifier=self.component_identifier,
                                                    dataset_name=self.dataset_identifier,
                                                    dataset_tag=split_name,
                                                    iterator_meta=iterator_meta)
        dataset_dict = {split_name: ModelGymInformedIteratorFactory.get_dataset_iterator(wiki_dataset, dataset_meta)}
        return dataset_dict


@dataclass
class GPT2LLMCollator(Collator):

    def __init__(self, target_publication_key: str, tokenizer_file_path: str, pad_to_multiple_of: int = 8):
        self.target_publication_key = target_publication_key
        tokenizer = GPT2TokenizerFast(tokenizer_file=tokenizer_file_path)  # "trained_wiki_tokenizer/tokenizer.json"
        tokenizer.pad_token = tokenizer.eos_token
        self.data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer,
                                                             mlm=False,
                                                             pad_to_multiple_of=pad_to_multiple_of)

    def __call__(self, batch: List[torch.Tensor]) -> DatasetBatch:
        """
        :param batch: batch format [no_samples, height, width, channels]
        :return:
        """
        collated_batch = self.data_collator(batch)
        samples = collated_batch["input_ids"]
        targets = {self.target_publication_key: collated_batch["labels"],
                   "attention_mask": collated_batch["attention_mask"]}
        return DatasetBatch(targets=targets, tags=None, samples=samples)


@dataclass
class MyModelRegistryConstructable(ModelRegistryConstructable):
    def _construct_impl(self):
        super()._construct_impl()
        self.model_registry.add_class("llm_gpt2", GPT2LLM)
        return self.model_registry


class GPT2LLMBluePrint(BluePrint):
    def __init__(self, run_mode: RunMode, config: Dict, grid_search_id: str,
                 experiment_id: str, external_injection: Dict[str, Any] = None,
                 warm_start_epoch: int = 0):
        super().__init__(run_mode, config, grid_search_id, experiment_id, external_injection, warm_start_epoch)

    @staticmethod
    def construct_components(config: Dict, component_names: List[str], device: torch.device,
                             external_injection: Dict[str, Any] = None) -> Dict[str, Any]:
        if external_injection is not None:
            injection_mapping = {"id_gpt2_llm_collator": GPT2LLMCollator,
                                 "id_computation_device": device,
                                 **external_injection}
            injector = Injector(injection_mapping, raise_mapping_not_found=True)

        else:
            injection_mapping = {"id_gpt2_llm_collator": GPT2LLMCollator}
            injector = Injector(injection_mapping, raise_mapping_not_found=False)

        component_factory = ComponentFactory(injector)
        component_factory.register_component_type("MODEL_REGISTRY", "DEFAULT", MyModelRegistryConstructable)
        component_factory.register_component_type("DATASET_ITERATORS", "LMWikiBookCorpusDataset", LMWikiBookCorpusDatasetConstructable),
        component_factory.register_component_type("LOSS_FUNCTION_REGISTRY", "LM", LMLossFunctionRegistryConstructable)

        components = component_factory.build_components_from_config(config, component_names)
        return components

    def construct(self, device: torch.device = None) -> Dict[str, Any]:
        component_names = ["model", "trainer", "optimizer", "evaluator", "early_stopping_strategy", "checkpointing_strategy", "lr_scheduler"]
        components = GPT2LLMBluePrint.construct_components(self.config, component_names, device, self.external_injection)

        return components
