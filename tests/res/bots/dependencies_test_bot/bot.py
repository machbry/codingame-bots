import os
import math
from pathlib import Path
from os.path import join

import pandas as pd

from challengelibs.module import CONSTANT, function, Class
from challengelibs.another_module import AnotherClass


pi = math.pi
path = join(Path(os.getcwd()), "test")
df = pd.DataFrame()
cst = CONSTANT
function()
obj = Class()
another_obj = AnotherClass([1, 1, 1])
