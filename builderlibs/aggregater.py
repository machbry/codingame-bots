from pathlib import Path
from typing import List, Union
import ast

from .logger import Logger
from builderlibs.fileutils import PythonFile
from builderlibs.dependencies import LocalModule, Import, ImportFrom, Module
from .optimizer import ImportNodesRemover, add_nodes_at_the_beginning, optimize_imports_nodes

logger = Logger().get()


class LocalModuleReplacer(ast.NodeTransformer):
    def __init__(self, main_module: LocalModule, local_packages_paths: List[Path] = [],
                 local_modules_replaced: List[Module] = []):
        super().__init__()
        self._main_module = main_module
        self._local_packages_paths = local_packages_paths
        self._local_modules_replaced = local_modules_replaced

    @property
    def from_paths(self):
        return [self._main_module.file_path] + self._local_packages_paths

    def visit_ImportFrom(self, node: ast.ImportFrom) -> Union[ast.ImportFrom, ast.Module]:
        for from_path in self.from_paths:
            imported_module = ImportFrom(node=node, from_path=from_path).modules[0]
            if imported_module.is_local:
                if imported_module not in self._local_modules_replaced:
                    self._local_modules_replaced.append(imported_module)

                    target_path = imported_module.target
                    target_module_file = PythonFile(target_path)
                    local_module_to_import = LocalModule(target_module_file)

                    replacer = LocalModuleReplacer(main_module=local_module_to_import,
                                                   local_packages_paths=self._local_packages_paths,
                                                   local_modules_replaced=self._local_modules_replaced)

                    logger.info(f"Module {imported_module.name} imported from file at {target_path}")

                    return ast.fix_missing_locations(replacer.visit(local_module_to_import.tree))
                else:
                    return ast.Module(body=[], type_ignores=[])
        return node

    def visit_Import(self, node: ast.Import):
        for from_path in self.from_paths:
            imported_modules = Import(node=node, from_path=from_path).modules
            for module in imported_modules:
                if module.is_local:
                    raise ValueError(f"Statement import for local module not supported. Please use from ... import ... "
                                     f"instead to import {module.name} in file {from_path}.")
        return node


class ModuleAggregater:
    def __init__(self, main_module: LocalModule, local_packages_paths: List[Path] = []):
        self._main_module = main_module
        self._replacer = LocalModuleReplacer(main_module, local_packages_paths)
        self._imports_nodes_remover = ImportNodesRemover()

    def aggregate(self) -> ast.AST:
        aggregated_tree_raw = self._replacer.visit(self._main_module.tree)
        aggregated_tree = self._imports_nodes_remover.visit(aggregated_tree_raw)
        imports_nodes_optimized = optimize_imports_nodes(imports_nodes=self._imports_nodes_remover.removed_nodes)
        return ast.fix_missing_locations(add_nodes_at_the_beginning(tree=aggregated_tree,
                                                                    nodes=imports_nodes_optimized))

    def aggregate_to_source(self) -> str:
        return ast.unparse(self.aggregate())
