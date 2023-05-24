import yaml
from typing import Dict


class YAMLConfigLoader:

    @staticmethod
    def load(path: str):
        with open(path, "r") as f:
            config: Dict = yaml.safe_load(f)
            if "global_config" in config:
                config.pop("global_config")
        return config

    @staticmethod
    def load_string(config_string: str):
        config: Dict = yaml.safe_load(config_string)
        if "global_config" in config:
            config.pop("global_config")
        return config
