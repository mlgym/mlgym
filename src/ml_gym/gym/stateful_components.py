from abc import ABC
from typing import Dict, Any, List


class StatefulComponent(ABC):
    """ Provides methods to set and get the temporary state of the object necessary to recreate it.
    """

    def set_state(self, state: Dict[str, Any]):
        """ Sets the the state of all attributes having type `StatefulComponent`
        Args:
            state: state as nested dictionary
        """
        for attr in dir(self):
            if attr.startswith('__'):
                continue
            if self._is_stateful_attribute(attr):
                attr_reference = getattr(self, attr)
                attr_reference.set_state(state[str(attr)])
            elif self._is_list_attribute(attr) and str(attr) in state:
                attr_reference = getattr(self, attr)
                self._set_state_list_attribute(attr_reference, state[str(attr)])
            elif self._is_dict_attribute(attr) and str(attr) in state:
                attr_reference = getattr(self, attr)
                self._set_state_dict_attribute(attr_reference, state[attr])

    def get_state(self) -> Dict[str, Any]:
        """ Returns the state of all attributes having type `StatefulComponent`
        Returns: state as nested dictionary
        """
        state = {}
        for attr in dir(self):
            if attr.startswith('__'):
                continue
            if self._is_stateful_attribute(attr):
                state[str(attr)] = getattr(self, attr).get_state()
            elif self._is_list_attribute(attr):
                state_list = self._get_state_list_attribute(attr)
                if state_list:  # we don't want to have empty lists
                    state[str(attr)] = state_list
            elif self._is_dict_attribute(attr):
                state_dict = self._get_state_dict_attribute(attr)
                if state_dict:  # we don't want to have empty lists
                    state[str(attr)] = state_dict
        return state

    def _is_stateful_attribute(self, attr) -> bool:
        """ Checks if attribute is of type `StatefulComponent`

        Args:
            attr: attribute contained in self

        Returns: True if attribute is of type `StatefulComponent`, False otherwise.
        """
        attr_reference = getattr(self, attr)
        return not attr.startswith('__') and isinstance(attr_reference, StatefulComponent)

    def _get_state_list_attribute(self, list_attr) -> List[Dict[str, Any]]:
        attr_list_reference = getattr(self, list_attr)
        return [element.get_state() for element in attr_list_reference if isinstance(element, StatefulComponent)]

    def _set_state_list_attribute(self, attr_list_reference, states: List[Dict[str, Any]]):
        counter = 0
        for element in attr_list_reference:
            if isinstance(element, StatefulComponent):
                element.set_state(states[counter])
                counter += 1

    def _get_state_dict_attribute(self, dict_attr) -> Dict[str, Any]:
        dict_attr_reference = getattr(self, dict_attr)
        return {key: value.get_state() for key, value in dict_attr_reference.items() if
                isinstance(value, StatefulComponent)}

    def _set_state_dict_attribute(self, dict_attr_reference, states: Dict[str, Any]):
        for key, value in dict_attr_reference.items():
            if isinstance(value, StatefulComponent):
                value.set_state(states[key])

    def _is_list_attribute(self, attr) -> bool:
        """Checks if instance attribute is of type iterable, e.g., list.

        Args:
            attr:

        Returns:

        """
        attr_reference = getattr(self, attr)
        return isinstance(attr_reference, list) and not attr.startswith('__')

    def _is_dict_attribute(self, attr) -> bool:
        attr_reference = getattr(self, attr)
        return isinstance(attr_reference, dict) and not attr.startswith('__')
