from typing import Any, Type
from collections.abc import Mapping


class ClassRegistry(Mapping):
    """A decorated dictionary to act as a model registry"""

    def __init__(self):
        '''Use the object dict'''
        self._store = {}

    def __setitem__(self, key, value):
        self._store[key] = value

    def __getitem__(self, key) -> Type:
        return self._store[key]

    def __delitem__(self, key):
        del self._store[key]

    def __iter__(self):
        return iter(self._store)

    def __len__(self):
        return len(self._store)

    def __str__(self):
        '''returns simple dict representation of the mapping'''
        return str(self._store)

    def __repr__(self):
        '''echoes class, id, & reproducible representation in the REPL'''
        return '{}, ClassRegistry({})'.format(super(ClassRegistry, self).__repr__(), self._store)

    def add_class(self, key: str, element: Type):
        self._store[key] = element

    def get_instance(self, key: str, **params) -> Any:
        return self._store[key](**params)


if __name__ == "__main__":
    class Example:
        def __init__(self, val: int):
            self.val = val

    registry = ClassRegistry()
    registry.add("example_key", Example)
    example = registry.get(key="example_key", configs={"val": 10}) # TODO make this a test
