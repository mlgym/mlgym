from copy import deepcopy
from typing import List

import numpy as np
import pytest
from ml_gym.batching.batch import InferenceResultBatch
from ml_gym.gym.post_processing import PredictPostProcessingIF, BinarizationPostProcessorImpl, DummyPostProcessorImpl
from ml_gym.gym.predict_postprocessing_component import PredictPostprocessingComponent

from pytests.test_env.inference_result_batch_fixtures import InferenceBatchResultFixture


class TestPredictPostProcessingComponent(InferenceBatchResultFixture):

    @pytest.fixture
    def post_processors(self, prediction_subscription_key: str, prediction_publication_key: str) -> List[
        PredictPostProcessingIF]:
        dummy_post_processor_impl = DummyPostProcessorImpl()
        argmax_post_processor_impl = BinarizationPostProcessorImpl(prediction_subscription_key,
                                                                   prediction_publication_key)

        return [dummy_post_processor_impl, argmax_post_processor_impl]

    @pytest.fixture
    def predict_post_preprocess_component(self) -> PredictPostprocessingComponent:
        predict_post_preprocess_component = PredictPostprocessingComponent()
        return predict_post_preprocess_component

    def test_post_process(self, predict_post_preprocess_component: PredictPostprocessingComponent,
                          inference_batch_result1: InferenceResultBatch,
                          post_processors: List[PredictPostProcessingIF],
                          prediction_subscription_key: str,
                          ):
        inference_batch_result_copy = deepcopy(inference_batch_result1)
        result_batch = predict_post_preprocess_component.post_process(inference_batch_result1, post_processors)
        assert not (result_batch.predictions[prediction_subscription_key].detach().cpu().numpy() ==
                    inference_batch_result_copy.predictions[prediction_subscription_key].detach().cpu().numpy()).all()
        assert (result_batch.predictions[prediction_subscription_key].detach().cpu().numpy() ==
                np.round(
                    inference_batch_result_copy.predictions[prediction_subscription_key].detach().cpu().numpy())).all()
