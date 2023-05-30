from ml_gym.loss_functions.loss_functions import LPLoss, CrossEntropyLoss, BCEWithLogitsLoss, BCELoss, NLLLoss, Loss  # , LPLossScaled
from typing import Dict
from ml_gym.batching.batch_filters import BatchFilter


class LossFactory:
    """
    Class containing all loss functions to be used by MlGym job models.
    """

    @staticmethod
    def get_lp_loss(target_subscription_key: str, prediction_subscription_key: str, root: int = 1, exponent: int = 2,
                    class_selection_fun_params: Dict = None, average_batch_loss: bool = True, tag: str = "") -> Loss:
        """
        Get Lp Loss object from params. 

        :params:
           - target_subscription_key (str): Loss function.
           - prediction_subscription_key (str): Prediction performed on the model.
           - root (int): Root Value in Loss equation.
           - exponent (int): Exponent value in Loss equation.
           - class_selection_fun_params (Dict): TO DO
           - average_batch_loss (bool): Average Loss value for the batch of data.
           - tag (str): Label to be tagged with the loss object. 

        :returns:
            LPLoss: Object of LPLoss.
        """
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
        """
        Get Cross Entropy Loss Object from params.

        :params:
           - target_subscription_key (str): Loss function.
           - prediction_subscription_key (str): Prediction performed on the model.
           - tag (str): Label to be tagged with the loss object. 

        :returns:
            CrossEntropyLoss: Object of CrossEntropyLoss.
        """
        return CrossEntropyLoss(target_subscription_key=target_subscription_key,
                                prediction_subscription_key=prediction_subscription_key,
                                tag=tag)

    @staticmethod
    def get_nll_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "") -> Loss:
        """
        Get Negative log Likelihood Loss Object from params.

        :params:
           - target_subscription_key (str): Loss function.
           - prediction_subscription_key (str): Prediction performed on the model.
           - tag (str): Label to be tagged with the loss object. 

        :returns:
            NLLLoss: Object of NLLLoss.
        """
        return NLLLoss(target_subscription_key=target_subscription_key,
                       prediction_subscription_key=prediction_subscription_key,
                       tag=tag)

    @staticmethod
    def get_bce_with_logits_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "",
                                 average_batch_loss: bool = True, flatten_predictions: bool = False) -> Loss:
        """
        Get BCEWithLogitsLoss Object (cross entropy loss that comes inside a sigmoid function) from params.

        :params:
           - target_subscription_key (str): Loss function.
           - prediction_subscription_key (str): Prediction performed on the model.
           - tag (str): Label to be tagged with the loss object.
           - average_batch_loss (bool): Average Loss value for the batch of data.
           - flatten_predictions (bool): Flatten the layer to get predictions.
           
        :returns:
            BCEWithLogitsLoss: Object of BCEWithLogitsLoss.
        """
        return BCEWithLogitsLoss(target_subscription_key=target_subscription_key,
                                 prediction_subscription_key=prediction_subscription_key,
                                 average_batch_loss=average_batch_loss,
                                 tag=tag,
                                 flatten_predictions=flatten_predictions)

    @staticmethod
    def get_bce_loss(target_subscription_key: str, prediction_subscription_key: str, tag: str = "",
                     average_batch_loss: bool = True) -> Loss:
        return BCELoss(target_subscription_key=target_subscription_key,
                       prediction_subscription_key=prediction_subscription_key,
                       average_batch_loss=average_batch_loss,
                       tag=tag)
