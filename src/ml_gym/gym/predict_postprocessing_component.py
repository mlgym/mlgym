from typing import List
from ml_gym.gym.post_processing import PredictPostProcessingIF
from ml_gym.batching.batch import InferenceResultBatch


class PredictPostprocessingComponent:

    @staticmethod
    def post_process(result_batch: InferenceResultBatch, post_processors: List[PredictPostProcessingIF]) -> InferenceResultBatch:
        """
        Perform prediction on the torch NN Model for the entire btach.

        :params:
           - result_batch (InferenceResultBatch): Predicttion performed on the model.
           - post_processors (List[PredictPostProcessingIF]): Batch number for which details to be logged.
           
        :returns:
            result_batch (InferenceResultBatch): Predicttion performed on the model.
        """
        for post_processor in post_processors:
            result_batch = post_processor.postprocess(result_batch)
        return result_batch
