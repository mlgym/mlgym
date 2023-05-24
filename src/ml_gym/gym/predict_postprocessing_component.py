from typing import List
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.batching.batch import InferenceResultBatch


class PredictPostprocessingComponent:

    @staticmethod
    def post_process(result_batch: InferenceResultBatch, post_processors: List[PredictPostProcessingIF]) -> InferenceResultBatch:
        for post_processor in post_processors:
            result_batch = post_processor.postprocess(result_batch)
        return result_batch
