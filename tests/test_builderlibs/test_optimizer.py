from builderlibs.optimizer import optimize_imports_nodes


def test_group_imports_nodes():
    # TODO : test group_imports_nodes
    pass


def test_optimize_imports_nodes(create_ast_imports_nodes_from_sources):
    imports_sources = ["from os.path import join",
                       "from pathlib import Path",
                       "from pathlib import PurePath",
                       "import math",
                       "from pathlib import Path",
                       "import pathlib",
                       "import pandas.util",
                       "import numpy as np",
                       "import os",
                       "import math",
                       "import os, datetime",
                       "import pandas as pd",
                       "import numpy",
                       "from dataclasses import dataclass as dc"]

    expected_imports_sources = ["from os.path import join",
                                "from pathlib import Path, PurePath",
                                "import math",
                                "import pathlib",
                                "import pandas.util",
                                "import numpy as np",
                                "import os",
                                "import datetime",
                                "import pandas as pd",
                                "import numpy",
                                "from dataclasses import dataclass as dc"]

    nodes = create_ast_imports_nodes_from_sources(imports_sources)
    expected_nodes = create_ast_imports_nodes_from_sources(expected_imports_sources)

    optimized_nodes = optimize_imports_nodes(nodes)

    assert len(expected_nodes) == len(optimized_nodes)

    # TODO : assert  optimized_nodes and expected_nodes are the same
