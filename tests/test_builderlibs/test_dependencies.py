import ast
from typing import Union
from pathlib import Path

import pytest

from builderlibs.challenge import ChallengeFolder
from builderlibs.dependencies import (Module, LocalModule, Import, ImportFrom, LocalModuleImportReplacer,
                                      ModuleAggregater)


BASE_PATH = Path(__file__).resolve()


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


@pytest.mark.parametrize("module_name, imported_from, level, relative_path_expected, is_local_expected", [
    ("math", "main_file", 0, None, False),
    ("os.path", "main_file", 0, None, False),
    ("challengelibs.module", "main_file", 0, "challengelibs/module.py", True),
    ("other_module", "libs_init_file", 0, "other_module.py", True),
    ("pandas", "libs_init_file", 0, None, False),
    ("sharedlibs.module", "main_file", 0, "../../sharedlibs/module.py", True),
    ("sharedlibs.module", "main_file", 2, "sharedlibs/module.py", True),
    ("challengelibs", "main_file", 0, "challengelibs", True),
    ("sharedlibs", "main_file", 0, "../../sharedlibs", True),
    ("unexistedlibs", "main_file", 0, None, False)
])
def test_module(module_name, imported_from, level, relative_path_expected, is_local_expected,
                dependencies_test_challenge):
    imported_from = getattr(dependencies_test_challenge.challenge_structure, imported_from).path
    module = Module(name=module_name, imported_from=imported_from, level=level)

    target = module.target
    assert target == imported_from.parent / relative_path_expected

    is_local = module.is_local
    assert is_local == is_local_expected


@pytest.mark.parametrize("source, modules_expected", [
    ("from pathlib import Path", [Module(name="pathlib", imported_from=BASE_PATH)]),
    ("import math", [Module(name="math", imported_from=BASE_PATH)]),
    ("import pandas as pd", [Module(name="pandas", imported_from=BASE_PATH, asname="pd")]),
    ("from challengelibs.module import function", [Module(name="challengelibs.module", imported_from=BASE_PATH)]),
    ("import os.path", [Module(name="os.path", imported_from=BASE_PATH)]),
    ("import ast, pytest", [Module(name="ast", imported_from=BASE_PATH),
                            Module(name="pytest", imported_from=BASE_PATH)]),
    ("from ..package import function, Class", [Module(name="package", imported_from=BASE_PATH, level=2)])
])
def test_import_statement(source, modules_expected, create_ast_import_node):
    node = create_ast_import_node(source)

    if isinstance(node, ast.Import):
        import_statement = Import(node=node, from_path=BASE_PATH)
    elif isinstance(node, ast.ImportFrom):
        import_statement = ImportFrom(node=node, from_path=BASE_PATH)
    else:
        raise TypeError(f"Unexpected path for node: {type(node)}.")

    assert import_statement.to_string() == source

    for i, module in enumerate(import_statement.modules):
        assert module == modules_expected[i]


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
