from ml_gym.loss_functions.loss_functions import LPLoss, LPLossScaled, CrossEntropyLoss, BCEWithLogitsLoss, NLLLoss
from ml_gym.batch import InferenceResultBatch
from typing import List, Dict
from functools import partial


def class_filter_selection_fun(inference_batch_result: InferenceResultBatch, selected_class: int, target_subscription_key: str) -> List[bool]:
    return (inference_batch_result.targets[target_subscription_key] == selected_class).tolist()


class LossFactory:

    @staticmethod
    def _get_sample_selection_fun(target_subscription_key: str, selected_class: int = None, ) -> callable:
        sample_selection_fun = partial(class_filter_selection_fun,
                                       selected_class=selected_class,
                                       target_subscription_key=target_subscription_key)
        return sample_selection_fun

    @staticmethod
    def get_lp_loss(target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2, class_selection_fun_params: Dict = None, tag: str = ""):
        sample_selection_fun = LossFactory._get_sample_selection_fun(
            **class_selection_fun_params) if class_selection_fun_params is not None else None
        return LPLoss(target_subscription_key, prediction_subscription_key, root, exponent, sample_selection_fun, tag)

    @staticmethod
    def get_scaled_lp_loss(target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2, class_selection_fun_params: Dict = None, tag: str = ""):
        sample_selection_fun = LossFactory._get_sample_selection_fun(
            **class_selection_fun_params) if class_selection_fun_params is not None else None
        return LPLossScaled(target_subscription_key, prediction_subscription_key, root, exponent, sample_selection_fun, tag)

    @staticmethod
    def get_cross_entropy_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = ""):
        return CrossEntropyLoss(target_subscription_key=target_subscription_key,
                                prediction_subscription_key=prediction_subscription_key,
                                tag=tag)

    @staticmethod
    def get_nll_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = ""):
        return NLLLoss(target_subscription_key=target_subscription_key,
                       prediction_subscription_key=prediction_subscription_key,
                       tag=tag)

    @staticmethod
    def get_bce_with_logits_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = ""):
        return BCEWithLogitsLoss(target_subscription_key=target_subscription_key,
                                 prediction_subscription_key=prediction_subscription_key,
                                 tag=tag)
