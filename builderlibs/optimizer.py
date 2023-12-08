import ast
from typing import Set


class ImportNodesRemover(ast.NodeTransformer):
    def __init__(self):
        self._removed_nodes: Set[ast.AST] = set()

    @property
    def removed_nodes(self) -> Set[ast.AST]:
        return self._removed_nodes

    def visit_ImportFrom(self, node: ast.ImportFrom):
        self._removed_nodes.add(node)

    def visit_Import(self, node: ast.Import):
        self._removed_nodes.add(node)


def add_nodes_at_the_beginning(tree: ast.AST, nodes: Set[ast.AST]) -> ast.AST:
    for node in nodes:
        tree.body.insert(0, node)
    return tree
