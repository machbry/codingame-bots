from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import ast

from builderlibs.fileutils import PythonFile


@dataclass
class Module:
    name: str
    imported_from: Path
    level: int = 0
    asname: str = None

    @property
    def target(self) -> Path:
        target = self.imported_from
        for _ in range(self.level + 1):
            target = target.parent
        return (target / (self.name.replace(".", "/") + ".py")).resolve()

    @property
    def is_local(self) -> bool:
        return self.target.exists()


class LocalModule:
    def __init__(self, python_file: PythonFile):
        self._file_path = python_file.path

    @property
    def file_path(self) -> Path:
        return self._file_path

    @property
    def tree(self) -> ast.Module:
        with open(self._file_path, 'r') as f:
            return ast.parse(f.read())

    def __repr__(self):
        return ast.dump(node=self.tree, include_attributes=True, indent=4)


class ImportStatement:
    def __init__(self, node: Union[ast.Import, ast.ImportFrom], from_path: Path):
        self._node = node
        self._from_path = from_path
        self._level = 0

    def to_string(self) -> str:
        return ast.unparse(self._node)


class Import(ImportStatement):
    def __init__(self, node: ast.Import, from_path: Path):
        super().__init__(node=node, from_path=from_path)

    @property
    def modules(self) -> List[Module]:
        return [Module(name=alias.name, imported_from=self._from_path, level=self._level, asname=alias.asname)
                for alias in self._node.names]


class ImportFrom(ImportStatement):
    def __init__(self, node: ast.ImportFrom, from_path: Path):
        super().__init__(node=node, from_path=from_path)
        self._level = self._node.level

    @property
    def modules(self) -> List[Module]:
        return [Module(name=self._node.module, imported_from=self._from_path, level=self._level)]


class LocalModuleImportReplacer(ast.NodeTransformer):
    """
    A class used to replace local module imports with the corresponding module from the local package.

    Attributes:
        _main_module (LocalModule): The main module to replace local imports in.
        _local_packages_paths (List[Path]): A list of paths to local packages.
        _local_modules_replaced (List[LocalModule]): A list of local modules that have already been replaced.
    """

    def __init__(self, main_module: LocalModule, local_packages_paths: List[Path] = []):
        super().__init__()
        self._main_module = main_module
        self._local_packages_paths = local_packages_paths
        self._local_modules_replaced = []

    def visit_ImportFrom(self, node: ImportFrom) -> Union[ast.ImportFrom, ast.Module]:
        """
        Visits an ImportFrom node in the AST and replaces any local module imports with the corresponding
        module from the local package.

        Args:
            node (ast.ImportFrom): The ImportFrom node to visit.

        Returns:
            Union[ast.ImportFrom, ast.Module]: The modified ImportFrom node or an empty Module node if the
            imported module is not local.
        """
        from_paths = [self._main_module.file_path] + self._local_packages_paths

        for from_path in from_paths:
            imported_module = ImportFrom(node=node, from_path=from_path).modules[0]
            if imported_module.is_local:
                if (imported_module not in self._local_modules_replaced):
                    self._local_modules_replaced.append(imported_module)

                    target_path = imported_module.target
                    target_module_file = PythonFile(target_path)
                    local_module_to_import = LocalModule(target_module_file)

                    replacer = LocalModuleImportReplacer(main_module=local_module_to_import, local_packages_paths=self._local_packages_paths)

                    return ast.fix_missing_locations(replacer.visit(local_module_to_import.tree))
                else:
                    return ast.Module(body=[], type_ignores=[])

        return node

    def visit_Import(self, node: Import):
        """
        Visits an Import node in the AST and raises an error if the imported module is local.

        Args:
            node (ast.Import): The Import node to visit.

        Raises:
            ValueError: If the imported module is local.

        Returns:
            ast.Import: The original Import node.
        """
        main_module_path = self._main_module.file_path
        imported_modules = Import(node=node, from_path=main_module_path).modules

        for module in imported_modules:
            if module.is_local:
                raise ValueError(f"Statement import for local module not supported. Please use from ... import ... "
                                 f"instead to import {module.name} in file {main_module_path}.")

        return node


class ModuleAggregater:
    """
    A class that aggregates a main module and its local dependencies into a single AST.

    :param main_module: The main module to aggregate.
    :type main_module: LocalModule
    :param local_packages_paths: A list of paths to local packages that the main module depends on.
    :type local_packages_paths: List[Path]
    """

    def __init__(self, main_module: LocalModule, local_packages_paths: List[Path] = []):
        self._main_module = main_module
        self._replacer = LocalModuleImportReplacer(main_module, local_packages_paths)

    def aggregate(self) -> ast.AST:
        """
        Aggregates the main module's abstract syntax tree by visiting it with the replacer and fixing any missing locations.

        Returns:
            The aggregated abstract syntax tree.
        """
        return ast.fix_missing_locations(self._replacer.visit(self._main_module.tree))

    def aggregate_to_source(self) -> str:
        """
        Returns the source code representation of the AST node.

        :return: A string containing the source code representation of the AST node.
        :rtype: str
        """
        return ast.unparse(self.aggregate())
