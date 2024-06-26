import json
from pathlib import Path
import unittest

from botlibs.tree import Tree
from tests.constants import TESTS_BOTLIBS_PATH

TESTS_TREE_PATH = TESTS_BOTLIBS_PATH / "Tree"


def read_json(path: Path) -> dict:
    with open(path, 'r') as f:
        return json.load(f)


def tree_from_json(file_name: str) -> Tree:
    if file_name is None:
        return None
    return Tree(**read_json(TESTS_TREE_PATH / file_name))


class TestTree(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_child(self):
        scenarios = {"sc1": {"parent_tree": "tree_numeric_value_1.json",
                             "child_tree": "tree_numeric_value_2.json"},
                     "sc2": {"parent_tree": "tree_numeric_value_1.json",
                             "child_tree": None}}

        for scenario_name, scenario in scenarios.items():
            parent_tree = tree_from_json(scenario["parent_tree"])
            child_tree = tree_from_json(scenario["child_tree"])
            initial_parent_nb_children = len(parent_tree.children)
            parent_tree.add_child(child_tree)
            try:
                self.assertEqual(initial_parent_nb_children + 1, len(parent_tree.children))
            except AssertionError:
                print(scenario_name)
                raise


if __name__ == '__main__':
    unittest.main()
