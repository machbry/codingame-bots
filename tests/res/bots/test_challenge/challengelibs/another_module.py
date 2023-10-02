import os, datetime

import numpy as np

from other_module import usefull_function


ANOTHER_CONSTANT = "another_constant"


def now(self):
    return datetime.datetime.now()


def another_function():
    return os.getcwd()


class AnotherClass:
    def __init__(self, l: list):
        self.array = np.array(l)

    def my_function(self):
        return usefull_function(self)
