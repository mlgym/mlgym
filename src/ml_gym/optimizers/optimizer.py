from typing import Dict, Any, List, Type
from torch.optim.optimizer import Optimizer
from copy import deepcopy
from ml_gym.error_handling.exception import OptimizerNotInitializedError


class OptimizerAdapter(object):

    def __init__(self, optimizer_class: Type[Optimizer], optimizer_params: Dict = None):
        self._optimizer_class = optimizer_class
        self._optimizer_params = optimizer_params if optimizer_params is not None else {}

        self._optimizer: Optimizer = None
        self._state_dict = None

    def register_model_params(self, model_params: Dict, restore_state: bool = True):
        model_params_list = model_params.values()
        if not restore_state:
            self._optimizer = self._optimizer_class(**self._optimizer_params, params=model_params_list)
            return

        # since we instantiate a new optimizer when we register a model, we have to save and restore the optimizer state
        if self._optimizer is not None:
            state_dict = self.state_dict()
            self._optimizer = self._optimizer_class(**self._optimizer_params, params=model_params_list)
            self.load_state_dict(state_dict)
        else:
            self._optimizer = self._optimizer_class(**self._optimizer_params, params=model_params_list)
            if self._state_dict is not None:
                self._optimizer.load_state_dict(self._state_dict)
                self._state_dict = None

    def __getstate__(self):
        if self._optimizer is not None:
            return self._optimizer.__getstate__()
        else:
            return {}

    def __setstate__(self, state):
        if not hasattr(self, '_optimizer'):
            self._optimizer = None
        if self._optimizer is not None:
            self._optimizer.__setstate__(state)

    def __repr__(self):
        return self._optimizer.__repr__()

    def _hook_for_profile(self):
        self._optimizer._hook_for_profile()

    def state_dict(self) -> Dict[str, Any]:
        if self._optimizer is not None:
            return self._optimizer.state_dict()
        elif self._state_dict is not None:
            return self._state_dict
        else:
            raise OptimizerNotInitializedError("Cannot access state_dict, because internal optimizer was not instantiated.")

    def load_state_dict(self, state_dict: Dict):
        if self._optimizer is not None:
            self._optimizer.load_state_dict(state_dict)
        else:  # here we store the state_dict until we instantiate the optimizer
            self._state_dict = state_dict

    def zero_grad(self, set_to_none: bool = False):
        if self._optimizer is None:
            raise OptimizerNotInitializedError("Internal optimizer was not instantiated. Has a model been registered for this optimizer?")
        self._optimizer.zero_grad(set_to_none)

    def step(self, closure=None):
        if self._optimizer is None:
            raise OptimizerNotInitializedError("Internal optimizer was not instantiated. Has a model been registered for this optimizer?")
        self._optimizer.step(closure)

    def add_param_group(self, param_group):
        if self._optimizer is None:
            raise OptimizerNotInitializedError("Internal optimizer was not instantiated. Has a model been registered for this optimizer?")
        self._optimizer.add_param_group(param_group)

    @property
    def param_groups(self):
        return self._optimizer.param_groups

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, deepcopy(v, memo))
        return result


class OptimizerBundle(OptimizerAdapter):

    def __init__(self, optimizers: Dict[str, OptimizerAdapter], optimizer_key_to_param_key_filters: Dict[str, List[str]]):
        self.optimizers = optimizers
        self.optimizer_key_to_param_key_filters = optimizer_key_to_param_key_filters

    def register_model_params(self, model_params: Dict, restore_state: bool = True):
        for optimizer_key in self.optimizers.keys():
            parameter_key_filters = self.optimizer_key_to_param_key_filters[optimizer_key]
            model_params_filtered = {model_param_key: model_params[model_param_key]
                                     for key_filter in parameter_key_filters
                                     for model_param_key in model_params.keys()
                                     if key_filter in model_param_key}
            self.optimizers[optimizer_key].register_model_params(model_params=model_params_filtered, restore_state=restore_state)

    def __getstate__(self):
        return {i: optimizer.__getstate__() for i, optimizer in self.optimizers.items()}

    def __setstate__(self, state):
        for i, state_i in state.items():
            self.optimizers[i].__setstate__(state_i)

    def __repr__(self):
        return "\n\n".join([self.optimizer.__repr__()])

    def _hook_for_profile(self):
        raise NotImplementedError

    def state_dict(self) -> Dict[str, Any]:
        return {i: optimizer.state_dict() for i, optimizer in self.optimizers.items()}

    def load_state_dict(self, state_dict):
        for i, state_dict_i in state_dict.items():
            self.optimizers[i].load_state_dict(state_dict_i)

    def zero_grad(self, set_to_none: bool = False, optimizer_id: int = None):
        if optimizer_id is None:
            for _, optimizer in self.optimizers.items():
                optimizer.zero_grad(set_to_none)
        else:
            self.optimizers[optimizer_id].zero_grad(set_to_none)

    def step(self, closure=None, optimizer_id: int = None):
        if optimizer_id is None:
            for _, optimizer in self.optimizers.items():
                optimizer.step(closure)
        else:
            self.optimizers[optimizer_id].step(closure)

    def add_param_group(self, param_group):
        raise NotImplementedError
