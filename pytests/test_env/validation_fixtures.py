from datetime import datetime
from typing import Type, Dict, Any
import pytest
from ml_gym.io.config_parser import YAMLConfigLoader
from pytests.test_env.linear_net_blueprint import LinearBluePrint


class ValidationFixtures:

    @pytest.fixture
    def gs_cv_config_path(cls) -> str:
        # gs_cv_path = os.path.join(os.path.abspath('.'), "..", "test_env", "cross_validation/gs_config_cv.yml")
        gs_cv_path = "pytests/example_configs/cross_validation/gs_config_cv.yml"
        return gs_cv_path

    @pytest.fixture
    def gs_cv_config(self, gs_cv_config_path) -> Dict[str, Any]:
        gs_cv_config = YAMLConfigLoader.load(gs_cv_config_path)
        return gs_cv_config

    @pytest.fixture
    def cv_config_path(self) -> str:
        # cv_path = os.path.join(os.path.abspath('.'), "..", "test_env", "cross_validation/cv_config.yml")
        cv_path = "pytests/example_configs/cross_validation/cv_config.yml"
        return cv_path

    @pytest.fixture
    def cv_config(self, cv_config_path) -> Dict[str, Any]:
        cv_config = YAMLConfigLoader.load(cv_config_path)
        return cv_config

    @pytest.fixture
    def gs_config_path(self) -> str:
        # gs_path = os.path.join(os.path.abspath('.'), "..", "test_env", "grid_search/gs_config.yml")
        gs_path = "pytests/example_configs/grid_search/gs_config.yml"
        return gs_path

    @pytest.fixture
    def gs_config(self, gs_config_path) -> Dict[str, Any]:
        gs_config = YAMLConfigLoader.load(gs_config_path)
        return gs_config

    @pytest.fixture
    def gs_nested_cv_path(self) -> str:
        # gs_nested_cv_path = os.path.join(os.path.abspath('.'), "..", "test_env",
        #                                  "nested_cross_validation/gs_config_nested_cv.yml")
        gs_nested_cv_path = "pytests/example_configs/nested_cross_validation/gs_config_nested_cv.yml"
        return gs_nested_cv_path

    @pytest.fixture
    def gs_nested_cv_config(self, gs_nested_cv_path) -> Dict[str, Any]:
        gs_nested_cv_config = YAMLConfigLoader.load(gs_nested_cv_path)
        return gs_nested_cv_config

    @pytest.fixture
    def nested_cv_path(self) -> str:
        # nested_cv_path = os.path.join(os.path.abspath('.'), "..", "test_env",
        #                               "nested_cross_validation/nested_cv_config.yml")
        nested_cv_path = "pytests/example_configs/nested_cross_validation/nested_cv_config.yml"

        return nested_cv_path

    @pytest.fixture
    def nested_cv_config(self, nested_cv_path) -> Dict[str, Any]:
        nested_cv_config = YAMLConfigLoader.load(nested_cv_path)
        return nested_cv_config

    @pytest.fixture
    def grid_search_id(self) -> str:
        return datetime.now().strftime("%Y-%m-%d--%H-%M-%S")

    @pytest.fixture
    def log_dir_path(self) -> str:
        return "general_logging"

    @pytest.fixture
    def num_epochs(self) -> int:
        return 2

    @pytest.fixture
    def dashify_logging_path(self) -> str:
        return "dashify_logging"

    @pytest.fixture
    def blue_print_type(self) -> Type:
        return LinearBluePrint

    @pytest.fixture
    def num_folds(self) -> int:
        return 5

    @pytest.fixture
    def process_count(self) -> int:
        return 2

    @pytest.fixture
    def log_std_to_file(self) -> bool:
        return False

    @pytest.fixture
    def keep_interim_results(self):
        return False
