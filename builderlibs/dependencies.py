from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import ast

from builderlibs.fileutils import PythonFile


@dataclass
class Module:
    name: str = ""
    asname: str = None

    def _path_to_check(self, base_path: Path, level: int) -> Path:
        for _ in range(level + 1):
            base_path = base_path.parent
        return base_path / (self.name.replace(".", "/") + ".py")

    def is_local(self, base_path: Path, level: int = 0) -> bool:
        path_to_check = self._path_to_check(base_path=base_path, level=level)
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
