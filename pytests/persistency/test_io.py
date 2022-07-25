import pytest
from dashify.logging.dashify_logging import ExperimentInfo, DashifyLogger
from ml_gym.persistency.io import DashifyReader
import os


class TestDashifyReader:

    @pytest.fixture
    def experiment_info_full(self) -> ExperimentInfo:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_experiments/full")
        return ExperimentInfo(log_dir=full_path, subfolder_id="", model_name="", dataset_name="", run_id="")

    @pytest.fixture
    def experiment_info_light(self) -> ExperimentInfo:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_experiments/light")
        return ExperimentInfo(log_dir=full_path, subfolder_id="", model_name="", dataset_name="", run_id="")

    @pytest.fixture
    def experiment_info_corrupt_metrics(self) -> ExperimentInfo:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_experiments/corrupt_metrics")
        return ExperimentInfo(log_dir=full_path, subfolder_id="", model_name="", dataset_name="", run_id="")

    @pytest.fixture
    def experiment_info_corrupt_models(self) -> ExperimentInfo:
        full_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_experiments/corrupt_models")
        return ExperimentInfo(log_dir=full_path, subfolder_id="", model_name="", dataset_name="", run_id="")

    @pytest.mark.skip(reason="Not supported at the moment")
    def test_get_last_epoch_full(self, experiment_info_full):
        epoch = DashifyReader.get_last_epoch(experiment_info_full)
        assert epoch == 2

    @pytest.mark.skip(reason="Not supported at the moment")
    def test_get_last_epoch_light(self, experiment_info_light):
        epoch = DashifyReader.get_last_epoch(experiment_info_light)
        assert epoch == 2

    def test_get_last_epoch_corrupt_models(self, experiment_info_corrupt_models):
        with pytest.raises(Exception):
            DashifyReader.get_last_epoch(experiment_info_corrupt_models)

    def test_get_last_epoch_corrupt_metrics(self, experiment_info_corrupt_metrics):
        with pytest.raises(Exception):
            DashifyReader.get_last_epoch(experiment_info_corrupt_metrics)
