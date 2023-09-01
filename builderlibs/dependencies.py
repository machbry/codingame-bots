from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import ast


@dataclass
class Module:
    name: str
    asname: str = None

    def _path_to_check(self, imported_from: Path, level: int) -> Path:
        for _ in range(level + 1):
            imported_from = imported_from.parent
        return imported_from / (self.name.replace(".", "/") + ".py")

    def is_local(self, imported_from: Path, level: int) -> bool:
        path_to_check = self._path_to_check(imported_from=imported_from, level=level)
        return path_to_check.is_file()


class ImportStatement:
    def __init__(self, node: Union[ast.Import, ast.ImportFrom], file_path: Path):
        self._node = node
        self._file_path = file_path
        self._modules: List[Module] = []
        self._level = 0

    @property
    def modules(self) -> List[Module]:
        return self._modules

    def to_string(self) -> str:
        return ast.unparse(self._node)


class Import(ImportStatement):
    def __init__(self, node: ast.Import, file_path: Path):
        super().__init__(node=node, file_path=file_path)
        self._modules = [Module(name=alias.name, asname=alias.asname) for alias in self._node.names]


class ImportFrom(ImportStatement):
    def __init__(self, node: ast.ImportFrom, file_path: Path):
        super().__init__(node=node, file_path=file_path)
        self._modules = [Module(name=self._node.module)]
        self._level = self._node.level


# class LocalModule:
#     def __init__(self, file_path: Path):
#         self._file_path = file_path
#
#         with open(file_path, 'r') as f:
#             self._tree = ast.parse(f.read())
#
#         self._import_statements = []
#         for node in ast.walk(self._tree):
#             if isinstance(node, ast.Import):
#                 self._import_statements.append(Import(node=node, file_path=self._file_path))
#             elif isinstance(node, ast.ImportFrom):
#                 self._import_statements.append(ImportFrom(node=node, file_path=self._file_path))
#
#         with open(file_path, 'r') as f:
#             self._body = f.readlines()
#
#     @property
#     def import_statements(self) -> List[ImportStatement]:
#         return self._import_statements
#
#     @property
#     def body(self) -> List[str]:
#         return self._body
#
#     def __repr__(self):
#         return ast.dump(node=self._tree, include_attributes=True, indent=4)
