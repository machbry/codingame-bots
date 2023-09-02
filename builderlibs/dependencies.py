from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import ast

from builderlibs.fileutils import PythonFile


@dataclass
class Module:
    name: str = ""
    asname: str = None

    def target_path(self, base_path: Path, level: int = 0) -> Path:
        for _ in range(level + 1):
            base_path = base_path.parent
        return base_path / (self.name.replace(".", "/") + ".py")

    def is_local(self, base_path: Path, level: int = 0) -> bool:
        path_to_check = self.target_path(base_path=base_path, level=level)
        return path_to_check.is_file()


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
    def __init__(self, node: Union[ast.Import, ast.ImportFrom]):
        self._node = node
        self._level = 0

    def to_string(self) -> str:
        return ast.unparse(self._node)


class Import(ImportStatement):
    def __init__(self, node: ast.Import):
        super().__init__(node=node)

    @property
    def modules(self) -> List[Module]:
        return [Module(name=alias.name, asname=alias.asname) for alias in self._node.names]


class ImportFrom(ImportStatement):
    def __init__(self, node: ast.ImportFrom):
        super().__init__(node=node)
        self._level = self._node.level

    @property
    def modules(self) -> List[Module]:
        return [Module(name=self._node.module)]


class LocalModuleImportReplacer(ast.NodeTransformer):
    def __init__(self, main_module: LocalModule):
        super().__init__()
        self._main_module = main_module
        self._local_modules_replaced = []

    def visit_ImportFrom(self, node: ImportFrom) -> Union[ast.ImportFrom, ast.Module]:
        imported_module = ImportFrom(node=node).modules[0]
        main_module_path = self._main_module.file_path

        if ((imported_module not in self._local_modules_replaced) and
                imported_module.is_local(base_path=main_module_path)):
            self._local_modules_replaced.append(imported_module)

            target_path = imported_module.target_path(base_path=main_module_path)
            module_file = PythonFile(target_path)
            local_module_to_import = LocalModule(module_file)

            replacer = LocalModuleImportReplacer(main_module=local_module_to_import)

            return ast.fix_missing_locations(replacer.visit(local_module_to_import.tree))

        return node

    def visit_Import(self, node: Import):
        imported_modules = Import(node=node).modules
        main_module_path = self._main_module.file_path

        for module in imported_modules:
            if module.is_local(base_path=main_module_path):
                raise ValueError(f"Statement import for local module not supported. Please use from ... import ... "
                                 f"instead to import {module.name} in file {main_module_path}.")

        return node


class ModuleAggregater:
    def __init__(self, main_module: LocalModule):
        self._main_module = main_module

        self._replacer = LocalModuleImportReplacer(main_module)

    def aggregate(self) -> ast.AST:
        return ast.fix_missing_locations(self._replacer.visit(self._main_module.tree))

    def to_source(self) -> str:
        return ast.unparse(self.aggregate())
