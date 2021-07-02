import pytest
import torch
from ml_gym.batching.batch import InferenceResultBatch
from ml_gym.loss_functions.loss_functions import LPLoss, CrossEntropyLoss, NLLLoss, BCEWithLogitsLoss  # , LPLossScaled
import torch.nn as nn


class TestLPLossFunctions:
    target_key = "target_key"
    prediction_key = "prediction_key"
    batch_size = 10
    sample_size = 100

    @pytest.fixture
    def inference_batch_result_train(self) -> InferenceResultBatch:
        targets = torch.ones(size=[TestLPLossFunctions.batch_size, TestLPLossFunctions.sample_size])*2  # [batch_size, sample_size]
        predictions = torch.ones(size=[TestLPLossFunctions.batch_size, TestLPLossFunctions.sample_size])*3
        return InferenceResultBatch(targets={TestLPLossFunctions.target_key: targets}, predictions={TestLPLossFunctions.prediction_key: predictions}, tags=None)

    @pytest.fixture
    def inference_batch_result_test(self) -> InferenceResultBatch:
        targets = torch.ones(size=[TestLPLossFunctions.batch_size, TestLPLossFunctions.sample_size])*2  # [batch_size, sample_size]
        predictions = torch.ones(size=[TestLPLossFunctions.batch_size, TestLPLossFunctions.sample_size])*5
        return InferenceResultBatch(targets={TestLPLossFunctions.target_key: targets}, predictions={TestLPLossFunctions.prediction_key: predictions}, tags=None)

    @pytest.mark.parametrize("exponent,root, torch_loss_fun", [
        (2, 1, nn.MSELoss(reduction="sum")),  # squared L2 norm
        (1, 1, nn.L1Loss(reduction="sum"))  # L1 loss
    ])
    def test_lp_loss(self, exponent, root, torch_loss_fun, inference_batch_result_train):
        targets = inference_batch_result_train.targets[TestLPLossFunctions.target_key]
        predictions = inference_batch_result_train.predictions[TestLPLossFunctions.prediction_key]

        total_loss = (torch.sum((targets[0, :] - predictions[0, :]).abs()**exponent) ** (1/root)).sum()*TestLPLossFunctions.batch_size
        calc_loss = LPLoss(target_subscription_key=TestLPLossFunctions.target_key,
                           prediction_subscription_key=TestLPLossFunctions.prediction_key,
                           root=root,
                           exponent=exponent,
                           average_batch_loss=False)(inference_batch_result_train).sum()
        torch_loss = torch_loss_fun(predictions, targets)
        assert total_loss == calc_loss
        assert calc_loss == torch_loss

    def test_loss_selection(self, inference_batch_result_train):
        mask = ([True, False] * int(TestLPLossFunctions.batch_size))[:TestLPLossFunctions.batch_size]

        loss_fun = LPLoss(target_subscription_key=TestLPLossFunctions.target_key,
                          prediction_subscription_key=TestLPLossFunctions.prediction_key,
                          root=2,
                          exponent=2,
                          average_batch_loss=False,
                          sample_selection_fun=lambda inference_batch_result:  mask)
        assert len(loss_fun(inference_batch_result_train)) == sum(mask)

    # @pytest.mark.parametrize("exponent, root", [
    #     (2, 1),  # squared L2 norm
    #     (1, 1)  # L1 loss
    # ])
    # def test_scaled_lp_loss(self, exponent, root, inference_batch_result_train, inference_batch_result_test):
    #     targets_train = inference_batch_result_train.targets[TestLPLossFunctions.target_key]
    #     predictions_train = inference_batch_result_train.predictions[TestLPLossFunctions.prediction_key]
    #     targets_test = inference_batch_result_test.targets[TestLPLossFunctions.target_key]
    #     predictions_test = inference_batch_result_test.predictions[TestLPLossFunctions.prediction_key]

    #     reference_loss_train = (torch.sum((targets_train[0, :] - predictions_train[0, :]).abs()
    #                                       ** exponent)**1/root).sum()*TestLPLossFunctions.batch_size

    #     reference_loss_test = (torch.sum((targets_test[0, :] - predictions_test[0, :]).abs()
    #                                      ** exponent)**1/root).sum()*TestLPLossFunctions.batch_size

    #     loss_fun = LPLossScaled(target_subscription_key=TestLPLossFunctions.target_key,
    #                             prediction_subscription_key=TestLPLossFunctions.prediction_key,
    #                             root=root,
    #                             exponent=exponent)
    #     loss_fun.warm_up(inference_batch_result_train)
    #     loss_fun.finish_warmup()

    #     mean = loss_fun.scaler._mean
    #     loss_train = loss_fun(inference_batch_result_train).sum()
    #     loss_test = loss_fun(inference_batch_result_test).sum()

    #     assert loss_train*mean == reference_loss_train
    #     assert loss_test*mean == reference_loss_test


class TestClassificationLossFunctions:
    target_key = "target_key"
    prediction_key = "prediction_key"

    @pytest.fixture
    def cross_entropy_inference_batch_result(self) -> InferenceResultBatch:
        targets = torch.IntTensor([1, 1])  # [batch_size]
        predictions = torch.FloatTensor([[10, 0], [0, 10]])
        return InferenceResultBatch(targets={TestClassificationLossFunctions.target_key: targets},
                                    predictions={TestClassificationLossFunctions.prediction_key: predictions},
                                    tags=None)

    @pytest.fixture
    def bce_with_logits_inference_batch_result(self) -> InferenceResultBatch:
        targets = torch.IntTensor([1, 1])  # [batch_size]
        predictions = torch.FloatTensor([[10], [0]])
        return InferenceResultBatch(targets={TestClassificationLossFunctions.target_key: targets},
                                    predictions={TestClassificationLossFunctions.prediction_key: predictions},
                                    tags=None)

    def test_cross_entropy_loss(self, cross_entropy_inference_batch_result):
        ce_loss_fun = CrossEntropyLoss(target_subscription_key=TestLPLossFunctions.target_key,
                                       prediction_subscription_key=TestLPLossFunctions.prediction_key,
                                       average_batch_loss=False)
        loss = ce_loss_fun(cross_entropy_inference_batch_result)
        assert loss[0] > loss[1]

    def test_nllloss_loss(self, cross_entropy_inference_batch_result):
        # NOTE: Here we use the same inference batch as in the cross entropy loss, since in OUR implementation they are equal.
        ce_loss_fun = CrossEntropyLoss(target_subscription_key=TestLPLossFunctions.target_key,
                                       prediction_subscription_key=TestLPLossFunctions.prediction_key,
                                       average_batch_loss=False)
        nll_loss_fun = NLLLoss(target_subscription_key=TestLPLossFunctions.target_key,
                               prediction_subscription_key=TestLPLossFunctions.prediction_key)
        ce_loss = ce_loss_fun(cross_entropy_inference_batch_result)
        nll_loss = nll_loss_fun(cross_entropy_inference_batch_result)
        assert all(nll_loss == ce_loss)

    def test_bce_with_logits_loss(self, bce_with_logits_inference_batch_result):
        loss_fun = BCEWithLogitsLoss(target_subscription_key=TestLPLossFunctions.target_key,
                                     prediction_subscription_key=TestLPLossFunctions.prediction_key)
        loss = loss_fun(bce_with_logits_inference_batch_result)
        assert True
