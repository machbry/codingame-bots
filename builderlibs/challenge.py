from dataclasses import dataclass
from pathlib import Path
from typing import List

from builderlibs.fileutils import Node, Directory, PythonFile
from builderlibs.dependencies import LocalModule
from builderlibs.aggregater import ModuleAggregater


CHALLENGE_MAIN_FILE_NAME = "bot"
CHALLENGE_LIBS_NAME = "challengelibs"


@dataclass
class ChallengeStructure:
    _name: str
    _parent: Path
    _main_file_name: str = CHALLENGE_MAIN_FILE_NAME
    _libs_name: str = CHALLENGE_LIBS_NAME

    def __post_init__(self):
        if self._name in ["", None]:
            raise ValueError("_name attribute can't be None or an empty string.")

    @property
    def name(self):
        return self._name

    @property
    def root(self) -> Directory:
        return Directory(self._parent / self._name)

    @property
    def main_file(self) -> PythonFile:
        return PythonFile(self.root.path / self._main_file_name)

    @property
    def init_file(self) -> PythonFile:
        return PythonFile(self.root.path / "__init__.py")

    @property
    def libs(self) -> Directory:
        return Directory(self.root.path / self._libs_name)

    @property
    def libs_init_file(self) -> PythonFile:
        return PythonFile(self.libs.path / "__init__.py")

    @property
    def nodes(self) -> List[Node]:
        return [self.root, self.main_file, self.init_file, self.libs, self.libs_init_file]


class ChallengeFolder:
    def __init__(self, name: str, parent: Path):
        self._challenge_structure = ChallengeStructure(_name=name, _parent=parent)

    @property
    def challenge_structure(self) -> ChallengeStructure:
        return self._challenge_structure
    
    @property
    def main_module(self) -> LocalModule:
        return LocalModule(self.challenge_structure.main_file)

    @property
    def name(self) -> str:
        return self._challenge_structure.name

    def exists(self) -> bool:
        return any([node.exists() for node in self._challenge_structure.nodes])

    def make(self) -> None:
        [node.make() for node in self._challenge_structure.nodes]

    def destroy(self, force_destroy: bool = True) -> None:
        destroy = force_destroy
        if not force_destroy:
            root = self._challenge_structure.root.path
            print(f"Are you sure you want to delete \"{root}\" and all files inside ? (Y/n)")
            user_input = input()
            destroy = True if user_input == "Y" else False
        if destroy:
            [node.destroy() for node in self._challenge_structure.nodes]

    def aggregate_to_source(self, local_packages_paths: List[Path] = []) -> str:
        return ModuleAggregater(main_module=self.main_module, local_packages_paths=local_packages_paths).aggregate_to_source()
