import pytest
from ml_gym.registries.class_registry import ClassRegistry


class Example:
    def __init__(self, val: int):
        self.val = val


class TestClassRegistry:
    @pytest.fixture
    def class_registry(self):
        registry = ClassRegistry()
        return registry

    def test_setter_getter(self, class_registry):
        class_registry["example_key"] = Example
        example_class = class_registry.get(key="example_key")
        # check if the class is correct
        assert example_class == Example

    def test_get_instance(self, class_registry):
        class_registry.add_class("example_key2", Example)
        configs = {"val": 10}
        example_class2 = class_registry.get(key="example_key2")
        assert example_class2 == Example
        example_instance = class_registry.get_instance(key="example_key2", **configs)
        assert isinstance(example_instance, Example)
        assert example_instance.val == 10

    def test_iter(self, class_registry):
        class_registry["example_key"] = Example
        class_registry.add_class("example_key2", Example)
        for registry_key in class_registry:
            assert class_registry[registry_key] == Example

    def test_len(self, class_registry):
        class_registry["example_key"] = Example
        assert len(class_registry) == 1
        class_registry["example_key2"] = Example
        assert len(class_registry) == 2
        del class_registry["example_key2"]
        assert len(class_registry) == 1
