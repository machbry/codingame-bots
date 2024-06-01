from typing import Union, List
import ast

import pytest

from builderlibs.challenge import ChallengeFolder
from tests.constants import TESTS_BOTS_PATH


@pytest.fixture(scope="session")
def create_challenge_folder():

    folders_made = []

    def _create_challenge_folder(name: str, make: bool = False):
        challenge_folder = ChallengeFolder(name=name, parent=TESTS_BOTS_PATH)
        if make:
            challenge_folder.make()
            folders_made.append(challenge_folder)
        return challenge_folder

    yield _create_challenge_folder

    [folder.destroy() for folder in folders_made]


@pytest.fixture(scope="session")
def test_challenge(create_challenge_folder) -> ChallengeFolder:
    return create_challenge_folder(name="test_challenge")


@pytest.fixture
def create_ast_imports_nodes():
    def _create_ast_imports_nodes(source: str) -> List[Union[ast.Import, ast.ImportFrom]]:
        tree = ast.parse(source)
        imports_nodes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                imports_nodes.append(node)
        return imports_nodes
    return _create_ast_imports_nodes


@pytest.fixture
def create_ast_imports_nodes_from_sources(create_ast_imports_nodes):
    def _create_ast_imports_nodes_from_sources(sources: List[str]) -> List[Union[ast.Import, ast.ImportFrom]]:
        concat_source = ""
        for source in sources:
            concat_source += source + "\n"
        nodes = create_ast_imports_nodes(concat_source)
        return nodes
    return _create_ast_imports_nodes_from_sources

