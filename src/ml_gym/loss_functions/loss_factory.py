from ml_gym.loss_functions.loss_functions import LPLoss, CrossEntropyLoss, BCEWithLogitsLoss, BCELoss, NLLLoss, Loss  # , LPLossScaled
from typing import Dict
from ml_gym.batching.batch_filters import BatchFilter


class LossFactory:

    @staticmethod
    def get_lp_loss(target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2,
                    class_selection_fun_params: Dict = None, average_batch_loss: bool = True, tag: str = "") -> Loss:
        sample_selection_fun = BatchFilter.get_class_selection_fun(
            **class_selection_fun_params) if class_selection_fun_params is not None else None
        return LPLoss(target_subscription_key, prediction_subscription_key, root, exponent, sample_selection_fun, tag, average_batch_loss)

    # @staticmethod
    # def get_scaled_lp_loss(target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2,
    #                        class_selection_fun_params: Dict = None, tag: str = "") -> Loss:
    #     sample_selection_fun = BatchFilter.get_class_selection_fun(**class_selection_fun_params) if class_selection_fun_params is not None else None
    #     return LPLossScaled(target_subscription_key, prediction_subscription_key, root, exponent, sample_selection_fun, tag)

    @staticmethod
    def get_cross_entropy_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "") -> Loss:
        return CrossEntropyLoss(target_subscription_key=target_subscription_key,
                                prediction_subscription_key=prediction_subscription_key,
                                tag=tag)

    @staticmethod
    def get_nll_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "") -> Loss:
        return NLLLoss(target_subscription_key=target_subscription_key,
                       prediction_subscription_key=prediction_subscription_key,
                       tag=tag)

    @staticmethod
    def get_bce_with_logits_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "",
                                 average_batch_loss: bool = True) -> Loss:
        return BCEWithLogitsLoss(target_subscription_key=target_subscription_key,
                                 prediction_subscription_key=prediction_subscription_key,
                                 average_batch_loss=average_batch_loss,
                                 tag=tag)

    @staticmethod
    def get_bce_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "",
                     average_batch_loss: bool = True) -> Loss:
        return BCELoss(target_subscription_key=target_subscription_key,
                       prediction_subscription_key=prediction_subscription_key,
                       average_batch_loss=average_batch_loss,
                       tag=tag)
