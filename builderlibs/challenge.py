from dataclasses import dataclass
from pathlib import Path
from typing import List

from builderlibs.fileutils import Node, Directory, PythonFile


CHALLENGE_MAIN_FILE_NAME = "bot"
CHALLENGE_LIBS_NAME = "challengelibs"


@dataclass
class ChallengeStructure:
    _name: str
    _parent: Path
    _main_file_name: str = CHALLENGE_MAIN_FILE_NAME
    _libs_name: str = CHALLENGE_LIBS_NAME

    @property
    def root(self) -> Directory:
        return Directory(self._parent / self._name)

    @property
    def main_file(self) -> PythonFile:
        return PythonFile(self.root.path / self._main_file_name)

    @property
    def libs(self) -> Directory:
        return Directory(self.root.path / self._libs_name)

    @property
    def libs_init_file(self) -> PythonFile:
        return PythonFile(self.libs.path / "__init__.py")

    @property
    def nodes(self) -> List[Node]:
        return [self.root, self.main_file, self.libs, self.libs_init_file]


class ChallengeFolder:
    def __init__(self, name: str, parent: Path):
        self._challenge_structure = ChallengeStructure(_name=name, _parent=parent)

    def exists(self) -> bool:
        return all([node.exists() for node in self._challenge_structure.nodes])

    def make(self) -> None:
        [node.make() for node in self._challenge_structure.nodes]

    def destroy(self) -> None:
        [node.destroy() for node in self._challenge_structure.nodes]
