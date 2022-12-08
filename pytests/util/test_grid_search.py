import os
from typing import List, Tuple, Any, Dict

import pytest
from ml_gym.util.grid_search import GridSearch


class TestGridSearch:
    @pytest.fixture
    def keys(self) -> List[str]:
        keys = ["a", "b"]
        return keys

    @pytest.fixture
    def values(self) -> Tuple[Any]:
        values = (1, 2)
        return values

    @pytest.fixture
    def splits_by_keys(self) -> Dict[str, List[Any]]:
        splits_by_keys = {"p1": ["A", "B"], "p2": [1]}
        return splits_by_keys

    @pytest.fixture
    def node(self) -> Dict[str, Any]:
        return {
            "p_1": 1,
            "p_2": {
                "sweep": "absolute",
                "values": [
                    2,
                    3,
                    4
                ]
            },
            "p_3": {
                "sweep": "absolute",
                "values": [
                    {
                        "p_3.1": "XYZ"
                    },
                    {
                        "p_3.1": {
                            "sweep": "absolute",
                            "values": [
                                6,
                                7
                            ]
                        }
                    }
                ]
            },
            "p_4": [12, 13]
        }

    @pytest.fixture
    def config_path(self) -> str:
        return "example/grid_search/gs_config.yml"

    def test_get_dict_obj(self, keys: List[str], values: Tuple[Any]):
        d = GridSearch._get_dict_obj(keys, values)
        assert d[keys[0]] == values[0] and d[keys[1]] == values[1]

    def test_find_products(self, splits_by_keys: Dict[str, List[Any]]):
        dict_objs = GridSearch._find_products(splits_by_keys)
        assert dict_objs[0]["p1"] == "A"
        assert dict_objs[1]["p1"] == "B"
        assert dict_objs[0]["p2"] == dict_objs[1]["p2"] == 1

    def test_split_config(self, node: Dict[str, Any]):
        configs = GridSearch._split_config(node)
        assert len(configs) == 9
        assert not GridSearch._is_config_equal(configs[0], configs[1])
        assert GridSearch._is_config_equal(configs[0], configs[0])

        for config in configs:
            assert GridSearch.is_config_in_gs(config, node)
        assert not GridSearch.is_config_in_gs({'p_1': 1, 'p_2': 2, 'p_4': [13, 13]}, node)

        c = configs[0]
        c_negligible = {'p_3': {'p_3.1': None}, 'p_1': None, 'p_4': [12, None]}
        GridSearch._delete_branches(c, c_negligible)
        assert GridSearch._is_config_equal(c, c)

    def test_create_gs_configs_from_path(self, config_path):
        configs = GridSearch.create_gs_configs_from_path(config_path)
        assert configs[0]['optimizer']['config']['params']['lr'] == 0.01
        assert configs[1]['optimizer']['config']['params']['lr'] == 0.001
        assert configs[2]['optimizer']['config']['params']['lr'] == 0.0001
