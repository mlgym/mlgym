import os.path

import pytest
from typing import Dict, Any
from ml_gym.io.config_parser import YAMLConfigLoader
from ml_gym.blueprints.component_factory import Injector
import json


class TestInjector:
    @pytest.fixture
    def example_config(self) -> Dict[str, Any]:
        return YAMLConfigLoader.load(
            os.path.join("pytest/blueprints/component_factory/example_config.yml"))

    @pytest.fixture
    def example_config_injected(self) -> Dict[str, Any]:
        return YAMLConfigLoader.load(
            os.path.join("pytest/blueprints/component_factory/example_config_injected.yml"))

    @pytest.fixture
    def example_injection(self) -> Dict[str, Any]:
        return YAMLConfigLoader.load(
            os.path.join("pytest/blueprints/component_factory/example_injection.yml"))

    def test_constructable(self, example_config: Dict[str, Any], example_config_injected: Dict[str, Any],
                           example_injection: Dict[str, Any]):
        injector = Injector(mapping=example_injection)
        example_config_after_injection = injector.inject_pass(example_config)
        assert json.dumps(example_config_after_injection) == json.dumps(example_config_injected)
