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

    def __post_init__(self):
        self._is_local = False
        self._target = None

    def look_for_target(self):
        base_target = self.imported_from
        for _ in range(self.level + 1):
            base_target = base_target.parent

        dir_target = (base_target / (self.name.replace(".", "/"))).resolve()
        py_target = (base_target / (self.name.replace(".", "/") + ".py")).resolve()
        possible_targets = [dir_target, py_target]

        for possible_target in possible_targets:
            if possible_target.exists():
                self._target = possible_target
                self._is_local = True

    @property
    def target(self) -> Path:
        self.look_for_target()
        return self._target

    @property
    def is_local(self) -> bool:
        self.look_for_target()
        return self._is_local


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
    