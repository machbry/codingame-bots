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


class UsedVisitor(ast.NodeVisitor):
    def __init__(self):
        self.used_functions_and_classes = set()
        for builtin_method in dir(object):
            self.used_functions_and_classes.add(builtin_method)
        
    def visit(self, node):
        super().visit(node)
        for child in ast.iter_child_nodes(node):
            self.visit(child)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            self.used_functions_and_classes.add(node.func.id)

    def visit_ClassDef(self, node):
        for base in node.bases:
            if isinstance(base, ast.Name):
                self.used_functions_and_classes.add(base.id)
        for ast_node in node.body:
            if isinstance(ast_node, ast.FunctionDef):
                self.used_functions_and_classes.add(ast_node.name)

    def visit_Name(self, node):
        self.used_functions_and_classes.add(node.id)


class UnusedRemover(ast.NodeTransformer):
    def __init__(self, used_functions_and_classes):
        self.used_functions_and_classes = used_functions_and_classes

    def visit_FunctionDef(self, node):
        if node.name not in self.used_functions_and_classes:
            return None
        return node

    def visit_ClassDef(self, node):
        if node.name not in self.used_functions_and_classes:
            return None
        return node
