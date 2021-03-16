from typing import Any, Dict, List, Callable
from data_stack.dataset.iterator import DatasetIteratorIF, CombinedDatasetIterator
from ml_gym.data_handling.postprocessors.postprocessor import LabelMapperPostProcessor, FeatureEncoderPostProcessor, OneHotEncodedTargetPostProcessor
from ml_gym.data_handling.iterators import PostProcessedDatasetIterator
from data_stack.dataset.meta import MetaFactory
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from data_stack.dataset.splitter import SplitterFactory


class ModelGymInformedIteratorFactory(InformedDatasetFactory):

    @staticmethod
    def get_mapped_labels_iterator(identifier: str, iterator: DatasetIteratorIF, mappings: Dict) -> InformedDatasetIteratorIF:
        label_mapper_post_processor = LabelMapperPostProcessor(mappings=mappings,
                                                               target_position=iterator.dataset_meta.target_pos,
                                                               tag_position=iterator.dataset_meta.tag_pos)
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_dataset_iterator(PostProcessedDatasetIterator(iterator, label_mapper_post_processor), meta)

    @staticmethod
    def get_filtered_labels_iterator(identifier: str, iterator: InformedDatasetIteratorIF,
                                     filtered_labels: List[Any]) -> InformedDatasetIteratorIF:
        valid_indices = [i for i in range(len(iterator)) if iterator[i][iterator.dataset_meta.target_pos] in filtered_labels]
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_dataset_iterator_view(iterator, meta, valid_indices)

    @staticmethod
    def get_iterator_view(identifier: str, iterator: InformedDatasetIteratorIF, selection_fun: Callable[[DatasetIteratorIF], List[int]],
                          view_tags: Dict[str, Any]) -> InformedDatasetIteratorIF:
        valid_indices = selection_fun(iterator)
        # valid_indices = list(np.argwhere(valid_mask).flatten())
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_dataset_iterator_view(iterator, meta, valid_indices, view_tags)

    @staticmethod
    def get_feature_encoded_iterators(identifier: str, iterators: Dict[str, InformedDatasetIteratorIF],
                                      feature_encoding_configs: Dict[str, List[Any]]) -> Dict[str, DatasetIteratorIF]:
        sample_position = list(iterators.items())[0][1].dataset_meta.sample_pos
        feature_encoder_post_processor = FeatureEncoderPostProcessor(
            sample_position=sample_position, feature_encoding_configs=feature_encoding_configs)
        feature_encoder_post_processor.fit(iterators)
        return {name: InformedDatasetFactory.get_dataset_iterator(PostProcessedDatasetIterator(iterator, feature_encoder_post_processor),
                                                                  MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta,
                                                                                                             identifier=identifier))
                for name, iterator in iterators.items()}

    @staticmethod
    def get_one_hot_encoded_target_iterators(identifier: str, iterators: Dict[str, InformedDatasetIteratorIF],
                                             target_vector_size: int) -> Dict[str, DatasetIteratorIF]:
        target_position = list(iterators.items())[0][1].dataset_meta.target_pos
        postprocessor = OneHotEncodedTargetPostProcessor(target_vector_size=target_vector_size, target_position=target_position)
        return {name: InformedDatasetFactory.get_dataset_iterator(PostProcessedDatasetIterator(iterator, postprocessor), MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier))
                for name, iterator in iterators.items()}

    @staticmethod
    def get_combined_iterators(identifier: str, iterators: Dict[str, Dict[str, InformedDatasetIteratorIF]], combine_configs: Dict) -> Dict[str, InformedDatasetIteratorIF]:
        """Combines iterators.

        Args:
            identifier (str):
            iterators (Dict[str, Dict[str, InformedDatasetIteratorIF]]): Dictionary mapping from iterator_name -> split_name -> iterator
            combine_configs (Dict):

        Returns:
            Dict[str, InformedDatasetIteratorIF]:
        """

        def get_iterators_to_be_combined(iterators: Dict[str, Dict[str, InformedDatasetIteratorIF]], split_config: List):
            return [iterators[element["iterators_name"]][split_name] for element in split_config for split_name in element["splits"]]

        combined_iterators = {}
        for split_config in combine_configs:
            iterator_list = get_iterators_to_be_combined(iterators, split_config["old_splits"])
            meta = MetaFactory.get_dataset_meta_from_existing(dataset_meta=iterator_list[0].dataset_meta, identifier=identifier,
                                                              dataset_name="combined_dataset", dataset_tag=None)
            combined_iterators[split_config["new_split"]] = InformedDatasetFactory.get_dataset_iterator(
                CombinedDatasetIterator(iterator_list), meta)
        return combined_iterators

    @staticmethod
    def get_splitted_iterators(identifier: str, iterators: Dict[str, InformedDatasetIteratorIF], seed: int,
                               stratified: bool, split_config: Dict) -> Dict[str, InformedDatasetIteratorIF]:
        def _split(iterator: InformedDatasetIteratorIF, seed: int, split_config: Dict) -> Dict[str, InformedDatasetIteratorIF]:
            names = list(split_config.keys())
            ratios = list(split_config.values())
            if stratified:
                splitter = SplitterFactory.get_stratified_splitter(ratios=ratios, seed=seed)
            else:
                splitter = SplitterFactory.get_random_splitter(ratios=ratios, seed=seed)
            splitted_iterators = splitter.split(iterator)
            dataset_metas = [MetaFactory.get_dataset_meta_from_existing(
                iterator.dataset_meta, identifier=identifier, dataset_tag=name) for name in names]
            return {name: InformedDatasetFactory.get_dataset_iterator(splitted_iterators[i], dataset_metas[i]) for i, name in enumerate(names)}

        split_list = []
        for name, iterator in iterators.items():
            if name in split_config.keys():
                split_list.append(_split(iterator, seed, split_config[name]))
            else:
                split_list.append({name: iterator})

        splitted_iterator_dict = {}
        for d in split_list:
            splitted_iterator_dict = {**splitted_iterator_dict, **d}
        return splitted_iterator_dict

    @staticmethod
    def get_in_memory_iterator(identifier: str, iterator: InformedDatasetIteratorIF) -> InformedDatasetIteratorIF:
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_in_memory_dataset_iterator(iterator, meta)
