import pytest
from ml_gym.blueprints.constructables import DatasetIteratorConstructable, Requirement
import tempfile
import shutil
from data_stack.repository.repository import DatasetRepository
from typing import Dict
from data_stack.dataset.iterator import InformedDatasetIteratorIF
from mocked_classes import MockedMNISTFactory


class TestDatasetIteratorConstructable:

    @pytest.fixture
    def tmp_folder_path(self) -> str:
        path = tempfile.mkdtemp()
        yield path
        shutil.rmtree(path)

    @pytest.fixture
    def repository(self):
        dataset_repository: DatasetRepository = DatasetRepository()
        dataset_repository.register("mnist", MockedMNISTFactory())
        return dataset_repository

    @pytest.fixture
    def requirements(self, repository) -> Dict[str, Requirement]:
        return {"repository": Requirement(components=repository)}

    def test_constructable(self, requirements):
        constructable = DatasetIteratorConstructable(component_identifier="iterator_component",
                                                     requirements=requirements,
                                                     dataset_identifier="mnist",
                                                     split_configs=[{"split": "train"}])
        iterators = constructable.construct()
        sample, target, tag = iterators["train"][0]
        assert list(sample.shape) == [28, 28]
        assert isinstance(target, int)
        assert isinstance(iterators["train"], InformedDatasetIteratorIF)
