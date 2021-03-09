from itertools import product
from typing import Dict, Any, List, Tuple
import json
import glob
import os
import copy
from ml_gym.io.config_parser import YAMLConfigLoader


class GridSearch:
    # GRID SEARCH CREATION
    @staticmethod
    def _get_dict_obj(keys: List[str], values: Tuple[Any]) -> Dict[str, Any]:
        """
        Merges two lists into a dictionary, where one acts as the keys and the other one as the values
        :param keys:
        :param values:
        :return:
        """
        d = {}
        for key, value in zip(keys, values):
            d[key] = value
        return d

    @staticmethod
    def _find_products(splits_by_keys: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """
        Takes a dictionary str -> List, calculates the cartesian product for the set of lists and then assigns each product
        the respective key.
        Example: {"p1": ["A", "B", "C"], "p2": ["a", "b"], "p3": [1]} then the cartesian product will produce
        [("A", "a", 1), ("A", "b", 1), ("B", "a", 1), ("B", "b", 1), ("C", "a", 1), ("C", "b", 1)].
        From each tuple we then create a dictionary resulting in the list of dictionaries
        [{"p1": "A", "p2": "a", "p3": 1}, ..., {"p1": "C", "p2": "b", "p3": 1}].

        :param splits_by_keys:
        :return:
        """
        values = list(splits_by_keys.values())
        keys = list(splits_by_keys.keys())
        if len(values) == 1:
            dict_objs = [GridSearch._get_dict_obj(keys, (value,)) for value in values[0]]
        else:
            product_values = product(*values)
            dict_objs = [GridSearch._get_dict_obj(keys, value) for value in product_values]
        return dict_objs

    @staticmethod
    def _is_sweep_node(node: Dict[str, Any]):
        """
        Checks if a given node is a sweep node
        :param node:
        :return:
        """
        return GridSearch._is_node(node) and "sweep" in node

    @staticmethod
    def _is_node(item):
        """
        Checks if a given item is a node. Otherwise it's a leave.
        :param item:
        :return:
        """
        return isinstance(item, dict)

    @staticmethod
    def _expand_sweep_node(node: Dict[str, Any]) -> Dict[str, Any]:
        """
        Depending on the sweep type, e.g., range or absolute, the given sweep node needs to be fully created.
        :param node:
        :return:
        """
        if node["sweep"] == "absolute":
            return node
        else:
            raise NotImplementedError("Other sweep types have not been implemented, yet!")

    @staticmethod
    def _split_config(node: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes a grid search dictionary or a node within a grid search and creates the corresponding list of configs.
        :param node:
        :return:
        """
        splits_by_key = {}
        for child_key, child in node.items():
            if GridSearch._is_sweep_node(child):  # sweep node
                child = GridSearch._expand_sweep_node(child)
                all_splits = []
                for item in child["values"]:  # for each element in the sweep
                    splits = GridSearch._split_config(item) if GridSearch._is_node(item) else [item]
                    all_splits.extend(splits)
                splits_by_key[child_key] = all_splits

            elif GridSearch._is_node(child):  # normal dictionary node
                splits_by_key[child_key] = GridSearch._split_config(child)
            else:  # leave node
                splits_by_key[child_key] = [child]

        configs = GridSearch._find_products(splits_by_key)
        return [copy.deepcopy(config) for config in configs]

    # GS creationu

    @staticmethod
    def create_gs_configs_from_path(config_path: str) -> List[Dict]:
        gs_config = YAMLConfigLoader.load(config_path)
        configs = GridSearch.create_gs_from_config_dict(gs_config)
        return configs

    @staticmethod
    def create_gs_from_config_dict(gs_config: Dict):
        configs = GridSearch._split_config(gs_config)
        return configs

    # CONFIG PART OF GS

    @staticmethod
    def is_config_in_gs(d: Dict, gs: Dict, negligible_paths: Dict = None) -> bool:
        if negligible_paths is None:
            negligible_paths = {}
        gs_configs = GridSearch._split_config(gs)
        for gs_config in gs_configs:
            if GridSearch._is_config_equal(d, gs_config, negligible_paths):
                return True
        return False

    @staticmethod
    def _delete_branches(d, negligible_paths):
        """
        negligible example:
        ```
        {
        "optimizer": {
           "lr": None,
            "weight_decays": [0.0001, 123],
            }
        }
        ```
        ---> sets path root->optimizer->lr in d to None.
        Args:
            d:
            negligible_paths:

        Returns:

        """
        if isinstance(negligible_paths, dict):
            for key in negligible_paths.keys():
                if negligible_paths[key] is not None:
                    GridSearch._delete_branches(d[key], negligible_paths[key])
                else:
                    if key in d:
                        d.pop(key)
        if isinstance(negligible_paths, list):
            for i, negligible_elem in enumerate(negligible_paths):
                if negligible_elem is None:
                    d.pop(i)
                else:
                    GridSearch._delete_branches(d[i], negligible_paths[i])

    @staticmethod
    def _is_config_equal(d1: Dict, d2: Dict, negligible_paths: Dict = None) -> bool:
        """
        NOTE: This only works with dictionaries that don't have sweeps...
        Args:
            d1:
            d2:
            negligible_paths:

        Returns:

        """

        def ordered(obj):
            if isinstance(obj, dict):
                return sorted((k, ordered(v)) for k, v in obj.items())
            if isinstance(obj, list):
                return sorted(ordered(x) for x in obj)
            else:
                return obj

        if negligible_paths is None:
            negligible_paths = {}
        d1, d2 = d1.copy(), d2.copy()
        GridSearch._delete_branches(d1, negligible_paths)
        GridSearch._delete_branches(d2, negligible_paths)
        return ordered(d1) == ordered(d2)

    # Update configs from GS

    @staticmethod
    def update_config_from_grid_search(old_config: Dict, gs: List[Dict], negligible_paths: Dict):
        for new_config in gs:
            if GridSearch._is_config_equal(old_config, new_config, negligible_paths):
                return new_config
        raise Exception("Config is not present in grid search!")

    @staticmethod
    def get_rerun_configs(old_configs: List[Dict], gs: Dict, negligible_paths: Dict) -> List[Dict[str, Any]]:
        gs_configs = GridSearch.create_gs_from_config_dict(gs)
        return [GridSearch.update_config_from_grid_search(old_config, gs_configs, negligible_paths) for old_config in
                old_configs]

    @staticmethod
    def are_sweeps_identical(gs_config_path: str, experiment_folder: str) -> bool:
        with open(gs_config_path, "r") as f:
            gs_config = json.load(f)
        gs_configs_list = GridSearch.create_gs_configs_from_path(gs_config_path)
        config_paths = glob.glob(os.path.join(experiment_folder, "**/config.json"), recursive=True)
        if len(gs_configs_list) != len(config_paths):
            print(f"GS lengths do not match! (gs: {len(gs_configs_list)} vs experiments: {len(config_paths)})")
            return False
        else:
            configs = []
            for path in config_paths:
                with open(path, "r") as f:
                    config = json.load(f)
                    configs.append(config)
            equal_map = [GridSearch.is_config_in_gs(d=config, gs=gs_config) for config in configs]
            print(equal_map)
            return all(equal_map)


if __name__ == "__main__":
    test_gs = {
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
    configs = GridSearch._split_config(test_gs)
    print(f" Total configs found: {len(configs)}")
    for config in configs:
        print(config)

    print(GridSearch._is_config_equal(configs[0], configs[1]))
    c = configs[0]
    c_negligible = {'p_3': {'p_3.1': None}, 'p_1': None, 'p_4': [12, None]}
    GridSearch._delete_branches(c, c_negligible)
    print(c)
    print(GridSearch._is_config_equal(c, c))
