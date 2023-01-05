import json
import os
from pathlib import Path

import unittest

from botlibs.tree import Tree

ABSPATH = Path(__file__).parent.resolve()
BASE_PATH = os.path.join(ABSPATH, "res/Tree")


class TreeTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_add_child(self):
        scenarios = {}
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
