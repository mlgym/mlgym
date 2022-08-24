from typing import Any, Type
from collections.abc import Mapping
from ml_gym.error_handling.exception import ClassRegistryKeyNotFoundError


class ClassRegistry(Mapping):
    """A decorated dictionary to act as a registry for models, loss functions etc."""

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
        if key not in self._store:
            raise ClassRegistryKeyNotFoundError(f"Key {key} not present in class registry!")
        try:
            obj = self._store[key](**params)
        except Exception as e:
            raise Exception(f"Error building {self._store[key]}") from e
        return obj

