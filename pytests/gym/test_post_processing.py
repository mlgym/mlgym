from copy import deepcopy

import numpy as np
import pytest
import torch
from ml_gym.batching.batch import InferenceResultBatch
from ml_gym.gym.post_processing import SoftmaxPostProcessorImpl, \
    ArgmaxPostProcessorImpl, MaxOrMinPostProcessorImpl, BinarizationPostProcessorImpl, SigmoidalPostProcessorImpl

from pytests.test_env.inference_result_batch_fixtures import InferenceBatchResultFixture


class TestPostProcessing(InferenceBatchResultFixture):
    @pytest.fixture
    def prediction_subscription_key(self, model_prediction_key_anchor: str) -> str:
        return model_prediction_key_anchor

    @pytest.fixture
    def prediction_publication_key(self, model_prediction_key_anchor: str) -> str:
        return model_prediction_key_anchor

    def test_softmax_post_processor_impl(self, inference_batch_result2: InferenceResultBatch,
                                         prediction_subscription_key: str,
                                         prediction_publication_key: str):
        softmax_post_processor_impl = SoftmaxPostProcessorImpl(prediction_subscription_key, prediction_publication_key)
        result_batch = softmax_post_processor_impl.postprocess(inference_batch_result2)
        # check the sum is 0 for each sample
        assert (np.sum(result_batch.predictions[prediction_subscription_key].detach().cpu().numpy(),
                       axis=1) - 1 < 1e-5).all()

    def test_argmax_post_processor_impl(self, inference_batch_result2: InferenceResultBatch,
                                        prediction_subscription_key: str,
                                        prediction_publication_key: str):
        inference_batch_result2_copy = deepcopy(inference_batch_result2).predictions[
            prediction_subscription_key].detach().cpu().numpy()
        argmax_post_processor_impl = ArgmaxPostProcessorImpl(prediction_subscription_key, prediction_publication_key)
        result_batch = argmax_post_processor_impl.postprocess(inference_batch_result2)
        result_batch = result_batch.predictions[prediction_subscription_key].detach().cpu().numpy()

        # check the sum is 0 for each sample
        assert ((np.argmax(inference_batch_result2_copy, axis=1) - result_batch) < 1e-5).all()

    @pytest.mark.parametrize('agg_fun', ["min", "max"])
    def test_max_or_min_post_processor_impl(self, inference_batch_result2: InferenceResultBatch,
                                            prediction_subscription_key: str,
                                            prediction_publication_key: str, agg_fun: str) -> MaxOrMinPostProcessorImpl:
        inference_batch_result2_copy = deepcopy(inference_batch_result2).predictions[
            prediction_subscription_key].detach().cpu().numpy()
        # agg_fun: min, max
        max_or_min_post_processor_impl = MaxOrMinPostProcessorImpl(prediction_subscription_key,
                                                                   prediction_publication_key,
                                                                   agg_fun)
        result_batch = max_or_min_post_processor_impl.postprocess(inference_batch_result2)
        result_batch = result_batch.predictions[prediction_subscription_key].detach().cpu().numpy()

        if agg_fun == "min":
            assert ((np.min(inference_batch_result2_copy, axis=1) - result_batch) < 1e-5).all()
        else:
            assert ((np.max(inference_batch_result2_copy, axis=1) - result_batch) < 1e-5).all()

    def test_binarization_post_processor_impl(self, inference_batch_result2: InferenceResultBatch,
                                              prediction_subscription_key: str,
                                              prediction_publication_key: str):
        inference_batch_result2_copy = deepcopy(inference_batch_result2).predictions[
            prediction_subscription_key].detach().cpu().numpy()
        binarization_post_processor_impl = BinarizationPostProcessorImpl(prediction_subscription_key,
                                                                         prediction_publication_key)
        result_batch = binarization_post_processor_impl.postprocess(inference_batch_result2)
        result_batch = result_batch.predictions[prediction_subscription_key].detach().cpu().numpy()

        assert ((np.round(inference_batch_result2_copy) - result_batch) < 1e-5).all()

    def test_sigmoidal_post_processor_impl(self, inference_batch_result2: InferenceResultBatch,
                                           prediction_subscription_key: str,
                                           prediction_publication_key: str):
        sigmoid_inference_batch_result2_copy = torch.sigmoid(deepcopy(inference_batch_result2).predictions[
                                                                 prediction_subscription_key]).detach().cpu().numpy()
        sigmoidal_post_processor_impl = SigmoidalPostProcessorImpl(prediction_subscription_key,
                                                                   prediction_publication_key)
        result_batch = sigmoidal_post_processor_impl.postprocess(inference_batch_result2)
        result_batch = result_batch.predictions[prediction_subscription_key].detach().cpu().numpy()
        assert ((sigmoid_inference_batch_result2_copy - result_batch) < 1e-5).all()
