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


class TypeHintRemover(ast.NodeTransformer):

    def visit_FunctionDef(self, node):
        # remove the return type definition
        node.returns = None
        # remove all argument annotations
        if node.args.args:
            for arg in node.args.args:
                arg.annotation = None
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node):
        if node.value is None:
            return node
        return ast.Assign([node.target], node.value)


def add_nodes_at_the_beginning(tree: ast.AST, nodes: List[ast.AST]) -> ast.AST:
    for node in nodes:
        tree.body.insert(0, node)
    return tree


def group_imports_nodes(nodes: List[Union[ast.Import, ast.ImportFrom]]) -> dict:
    sources_grouped = {"ImportFrom": {},
                       "Import": set()}
    for node in nodes:
        type_import = type(node).__name__
        for alias in node.names:
            alias_infos = (alias.name, alias.asname)
            if isinstance(node, ast.ImportFrom):
                package = node.module
                if package not in sources_grouped[type_import].keys():
                    sources_grouped[type_import][package] = set()
                sources_grouped[type_import][package].add(alias_infos)
            elif isinstance(node, ast.Import):
                sources_grouped[type_import].add(alias_infos)
    return sources_grouped


def optimize_imports_nodes(imports_nodes: List[Union[ast.Import, ast.ImportFrom]]) -> List[Union[ast.Import, ast.ImportFrom]]:
    optimized_nodes = []
    aliases_grouped = group_imports_nodes(imports_nodes)

    for package, aliases in aliases_grouped["ImportFrom"].items():
        source = f"from {package} import "
        for name, asname in aliases:
            source += f"{name} as {asname}, " if asname else f"{name}, "
        source = source[0:len(source)-2]
        optimized_nodes.append(ast.parse(source).body[0])

    for name, asname in aliases_grouped["Import"]:
        source = f"import {name} as {asname}" if asname else f"import {name}"
        optimized_nodes.append(ast.parse(source).body[0])

    return optimized_nodes

