import ast
from typing import Union

import pytest

from builderlibs.challenge import ChallengeFolder
from builderlibs.dependencies import (Module, LocalModule, Import, ImportFrom, LocalModuleImportReplacer,
                                      ModuleAggregater)


@pytest.fixture(scope="session")
def dependencies_test_challenge(create_challenge_folder) -> ChallengeFolder:
    return create_challenge_folder(name="dependencies_test_challenge")


@pytest.fixture
def create_ast_import_node():
    def _create_ast_import_node(source: str) -> Union[Import, ImportFrom]:
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                return node
    return _create_ast_import_node


@pytest.mark.parametrize("module_name, base_path, level, relative_path_expected, is_local_expected", [
    ("math", "main_file", 0, "math.py", False),
    ("os.path", "main_file", 0, "os/path.py", False),
    ("challengelibs.module", "main_file", 0, "challengelibs/module.py", True),
    ("other_module", "libs_init_file", 0, "other_module.py", True),
    ("pandas", "libs_init_file", 0, "pandas.py", False)
])
def test_module(module_name, base_path, level, relative_path_expected, is_local_expected,
                dependencies_test_challenge):
    base_path = getattr(dependencies_test_challenge.challenge_structure, base_path).path
    module = Module(name=module_name)

    path_to_check = module.target_path(base_path=base_path, level=level)
    assert path_to_check == base_path.parent / relative_path_expected

    is_local = module.is_local(base_path=base_path, level=level)
    assert is_local == is_local_expected


@pytest.mark.parametrize("source, modules_expected, level_expected", [
    ("from pathlib import Path", [Module(name="pathlib")], 0),
    ("import math", [Module(name="math")], 0),
    ("import pandas as pd", [Module(name="pandas", asname="pd")], 0),
    ("from challengelibs.module import function", [Module(name="challengelibs.module")], 0),
    ("import os.path", [Module(name="os.path")], 0),
    ("import ast, pytest", [Module(name="ast"), Module(name="pytest")], 0),
    ("from ..package import function, Class", [Module(name="package")], 2)
])
def test_import_statement(source, modules_expected, level_expected, create_ast_import_node):
    node = create_ast_import_node(source)

    if isinstance(node, ast.Import):
        import_statement = Import(node=node)
    elif isinstance(node, ast.ImportFrom):
        import_statement = ImportFrom(node=node)
    else:
        raise TypeError(f"Unexpected path for node: {type(node)}.")

    assert import_statement.to_string() == source

    for i, module in enumerate(import_statement.modules):
        assert module == modules_expected[i]

    assert import_statement._level == level_expected


@pytest.mark.parametrize("python_file", [
    "main_file",
    "libs_init_file"
])
def test_local_module(python_file, dependencies_test_challenge):
    python_file = getattr(dependencies_test_challenge.challenge_structure, python_file)
    local_module = LocalModule(python_file)

    assert local_module.file_path == python_file.path
    assert isinstance(local_module.tree, ast.Module)


def test_module_aggregater(dependencies_test_challenge):
    main_file = dependencies_test_challenge.challenge_structure.main_file
    main_module = LocalModule(main_file)

    aggregated_module = ModuleAggregater(main_module)
    print(aggregated_module.to_source())
