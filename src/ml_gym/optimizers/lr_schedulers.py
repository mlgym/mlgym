from ml_gym.optimizers.optimizer import OptimizerAdapter
from torch.optim.lr_scheduler import _LRScheduler
from typing import Type, Dict
from ml_gym.error_handling.exception import LRSchedulerNotInitializedError


class LRSchedulerAdapter(object):
    """
    LRSchedulerAdapter class uses LR Scheduler selected from LRSchedulerFactory as an Optimizer in mlGym Job.
    """
    def __init__(self, lr_scheduler_class: Type[_LRScheduler], lr_scheduler_params: Dict = None):

        self._lr_scheduler_class = lr_scheduler_class
        self._lr_scheduler_params = lr_scheduler_params if lr_scheduler_params is not None else {}

        self._lr_scheduler: _LRScheduler = None
        self._state_dict = None

    def register_optimizer(self, optimizer: OptimizerAdapter):
        """
        Since we instantiate a new optimizer when we register a model, we have to save and restore the optimizer state.
        :params:
            optimizer (OptimizerAdapter): OptimizerAdapter object.
        """
        if self._lr_scheduler is not None:
            state_dict = self.state_dict()
            self._lr_scheduler = self._lr_scheduler_class(optimizer=optimizer, **self._lr_scheduler_params)
            self.load_state_dict(state_dict)
        else:
            self._lr_scheduler = self._lr_scheduler_class(optimizer=optimizer, **self._lr_scheduler_params)
            if self._state_dict is not None:
                self._lr_scheduler.load_state_dict(self._state_dict)
                self._state_dict = None

    def state_dict(self):
        """Returns the state of the scheduler as a :class:`dict`.

        It contains an entry for every variable in self.__dict__ which
        is not the optimizer.
        """
        if self._lr_scheduler is not None:
            return self._lr_scheduler.state_dict()
        elif self._state_dict is not None:
            return self._state_dict
        else:
            raise LRSchedulerNotInitializedError("Cannot access state_dict, because internal lr scheduler was not instantiated.")

    def load_state_dict(self, state_dict):
        """Loads the schedulers state.

        Args:
            state_dict (dict): scheduler state. Should be an object returned
                from a call to :meth:`state_dict`.
        """
        if self._lr_scheduler is not None:
            self._lr_scheduler.load_state_dict(state_dict)
        else:  # here we store the state_dict until we instantiate the optimizer
            self._state_dict = state_dict

    def get_last_lr(self):
        """ Return last computed learning rate by current scheduler.
        """
        return self._lr_scheduler.get_last_lr()

    def get_lr(self):
        # Compute learning rate using chainable form of the scheduler
        return self._lr_scheduler.get_lr()

    def print_lr(self, is_verbose, group, lr, epoch=None):
        """Display the current learning rate.
        """
        return self._lr_scheduler.print_lr(is_verbose, group, lr, epoch)

    def step(self, epoch=None):
        self._lr_scheduler.step(epoch)


class DummyLRcheduler(LRSchedulerAdapter):
    def __init__(self, optimizer: OptimizerAdapter):
        pass

    def state_dict(self):
        return {}

    def load_state_dict(self, state_dict):
        return

    def get_last_lr(self):
        return -1

    def get_lr(self):
        return -1

    def print_lr(self, is_verbose, group, lr, epoch=None):

        return

    def step(self, epoch=None):
        pass
