from dataclasses import dataclass
from pathlib import Path
from typing import List, Union
import ast


@dataclass
class Module:
    name: str = ""
    asname: str = None

    def _path_to_check(self, base_path: Path, level: int) -> Path:
        for _ in range(level + 1):
            base_path = base_path.parent
        return base_path / (self.name.replace(".", "/") + ".py")

    def is_local(self, base_path: Path, level: int) -> bool:
        path_to_check = self._path_to_check(base_path=base_path, level=level)
        return path_to_check.is_file()


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
#                 self._import_statements.append(Import(node=node))
#             elif isinstance(node, ast.ImportFrom):
#                 self._import_statements.append(ImportFrom(node=node))
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
