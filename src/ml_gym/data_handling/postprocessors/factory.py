from typing import Any, Dict, List, Callable
from data_stack.dataset.iterator import DatasetIteratorIF, CombinedDatasetIterator
from ml_gym.data_handling.postprocessors.postprocessor import LabelMapperPostProcessor, FeatureEncoderPostProcessor
from ml_gym.data_handling.iterators import PostProcessedDatasetIterator
from data_stack.dataset.meta import MetaFactory
from data_stack.dataset.factory import InformedDatasetFactory
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from data_stack.dataset.splitter import SplitterFactory


class ModelGymInformedIteratorFactory(InformedDatasetFactory):

    @staticmethod
    def get_mapped_labels_iterator(identifier: str, iterator: DatasetIteratorIF, mappings: Dict) -> InformedDatasetIteratorIF:
        label_mapper_post_processor = LabelMapperPostProcessor(mappings=mappings, target_position=iterator.dataset_meta.target_pos)
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_dataset_iterator(PostProcessedDatasetIterator(iterator, label_mapper_post_processor), meta)

    @staticmethod
    def get_filtered_labels_iterator(identifier: str, iterator: InformedDatasetIteratorIF, filtered_labels: List[Any]) -> InformedDatasetIteratorIF:
        valid_indices = [i for i in range(len(iterator)) if iterator[i][iterator.dataset_meta.target_pos] in filtered_labels]
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_dataset_iterator_view(iterator, meta, valid_indices)

    @staticmethod
    def get_iterator_view(identifier: str, iterator: InformedDatasetIteratorIF, selection_fun: Callable[[DatasetIteratorIF], List[int]]) -> InformedDatasetIteratorIF:
        valid_indices = selection_fun(iterator)
        # valid_indices = list(np.argwhere(valid_mask).flatten())
        meta = MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier)
        return InformedDatasetFactory.get_dataset_iterator_view(iterator, meta, valid_indices)

    @staticmethod
    def get_feature_encoded_iterators(identifier: str, iterators: Dict[str, InformedDatasetIteratorIF], feature_encoding_configs: Dict[str, List[Any]]) -> Dict[str, DatasetIteratorIF]:
        sample_position = list(iterators.items())[0][1].dataset_meta.sample_pos
        feature_encoder_post_processor = FeatureEncoderPostProcessor(
            sample_position=sample_position, feature_encoding_configs=feature_encoding_configs)
        feature_encoder_post_processor.fit(iterators)
        return {name: InformedDatasetFactory.get_dataset_iterator(PostProcessedDatasetIterator(iterator, feature_encoder_post_processor), MetaFactory.get_dataset_meta_from_existing(iterator.dataset_meta, identifier=identifier))
                for name, iterator in iterators.items()}

    @staticmethod
    def get_combined_iterators(identifier: str, iterators: Dict[str, InformedDatasetIteratorIF], combine_configs: Dict) -> Dict[str, InformedDatasetIteratorIF]:
        def get_filtered_iterators(iterators: Dict[str, DatasetIteratorIF], split_names: List[str]) -> List[DatasetIteratorIF]:
            return [iterator for iterator_name, iterator in iterators.items() if iterator_name in split_names]

        def combined_iterator(identifier, combined_name, iterators) -> InformedDatasetIteratorIF:
            meta = MetaFactory.get_dataset_meta_from_existing(iterators[0].dataset_meta, dataset_tag=combined_name, identifier=identifier)
            return InformedDatasetFactory.get_dataset_iterator(CombinedDatasetIterator(iterators), meta)

        combined_iterators = {combined_name: combined_iterator(identifier, combined_name, get_filtered_iterators(iterators, split_names))
                              for combined_name, split_names in combine_configs.items()}
        return combined_iterators

    @staticmethod
    def get_splitted_iterators(identifier: str, iterators: Dict[str, InformedDatasetIteratorIF], split_config: Dict) -> Dict[str, InformedDatasetIteratorIF]:
        def _split(iterator: InformedDatasetIteratorIF, split_config: Dict) -> Dict[str, InformedDatasetIteratorIF]:
            names = list(split_config.keys())
            ratios = list(split_config.values())
            splitter = SplitterFactory.get_random_splitter(ratios=ratios)
            splitted_iterators = splitter.split(iterator)
            dataset_metas = [MetaFactory.get_dataset_meta_from_existing(
                iterator.dataset_meta, identifier=identifier, dataset_tag=name) for name in names]
            return {name: InformedDatasetFactory.get_dataset_iterator(splitted_iterators[i], dataset_metas[i]) for i, name in enumerate(names)}

        split_list = []
        for name, iterator in iterators.items():
            if name in split_config.keys():
                split_list.append(_split(iterator, split_config[name]))
            else:
                split_list.append({name: iterator})

        splitted_iterator_dict = {}
        for d in split_list:
            splitted_iterator_dict = {**splitted_iterator_dict, **d}
        return splitted_iterator_dict
