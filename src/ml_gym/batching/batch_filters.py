from ml_gym.batching.batch import InferenceResultBatch
from typing import List, Callable
from functools import partial


class BatchFilter:

    @staticmethod
    def _class_filter_selection_fun(inference_batch_result: InferenceResultBatch, selected_class: int,
                                    target_subscription_key: str) -> List[bool]:
        return (inference_batch_result.targets[target_subscription_key] == selected_class).tolist()

    @staticmethod
    def get_class_selection_fun(target_subscription_key: str, selected_class: int = None) -> Callable[[InferenceResultBatch], List[bool]]:
        sample_selection_fun = partial(BatchFilter._class_filter_selection_fun,
                                       selected_class=selected_class,
                                       target_subscription_key=target_subscription_key)
        return sample_selection_fun
