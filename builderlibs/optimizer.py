import ast
from typing import List, Union


class ImportNodesRemover(ast.NodeTransformer):
    def __init__(self):
        self._removed_nodes = []

    @property
    def removed_nodes(self) -> List[Union[ast.Import, ast.ImportFrom]]:
        return self._removed_nodes

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self._removed_nodes.append(node)

    def visit_Import(self, node: ast.Import):
        self._removed_nodes.append(node)


def add_nodes_at_the_beginning(tree: ast.AST, nodes: List[ast.AST]) -> ast.AST:
    for node in nodes:
        tree.body.insert(0, node)
    return tree


def optimize_imports_nodes(imports_nodes: List[Union[ast.Import, ast.ImportFrom]]) -> List[Union[ast.Import, ast.ImportFrom]]:
    return imports_nodes

