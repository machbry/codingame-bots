from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import ast


@dataclass
class Module:
    name: str
    asname: str = ""

    def _path_to_check(self, imported_from: Path, level: int) -> Path:
        for _ in range(level + 1):
            imported_from = imported_from.parent
        return imported_from / (self.name.replace(".", "/") + ".py")

    def is_local(self, imported_from: Path, level: int) -> bool:
        path_to_check = self._path_to_check(imported_from=imported_from, level=level)
        return path_to_check.is_file()


class ImportStatement:
    def __init__(self, ast_node: Union[ast.Import, ast.ImportFrom], file_path: Path):
        self._ast_node = ast_node
        self._file_path = file_path
        self._modules: List[Module] = []
        self._level = 0

    @property
    def modules(self) -> List[Module]:
        return self._modules


class Import(ImportStatement):
    def __init__(self, ast_node: ast.Import, file_path: Path):
        super().__init__(ast_node=ast_node, file_path=file_path)
        self._modules = [Module(name=alias.name, asname=alias.asname) for alias in self._ast_node.names]


class ImportFrom(ImportStatement):
    def __init__(self, ast_node: ast.ImportFrom, file_path: Path):
        super().__init__(ast_node=ast_node, file_path=file_path)
        self._modules = [Module(name=self._ast_node.module)]
        self._level = ast_node.level
