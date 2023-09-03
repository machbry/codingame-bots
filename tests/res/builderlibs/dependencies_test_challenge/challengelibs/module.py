import math
from pathlib import Path

from another_module import another_function
from another_module import AnotherClass


CONSTANT = "constant"


def function():
    return another_function()


class Class:
    def __init__(self):
        self.another_class = AnotherClass([1, 1, 1])
        self.point = math.nan
        self.path = Path(CONSTANT)
