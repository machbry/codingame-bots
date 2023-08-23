from dataclasses import dataclass
from pathlib import Path
from typing import List

from builderlibs.logger import Logger


CHALLENGE_MAIN_FILE_NAME = "bot"
CHALLENGE_LIBS_NAME = "challengelibs"

logger = Logger().get()


@dataclass
class ChallengeStructure:
    _name: str
    _parent: Path
    _main_file_name: str
    _libs_name: str

    @property
    def root(self) -> Path:
        return self._parent / self._name

    @property
    def main_file_path(self) -> Path:
        if not self._main_file_name.endswith('.py'):
            self._main_file_name += '.py'
        return self.root / self._main_file_name

    @property
    def libs_directory(self) -> Path:
        return self.root / self._libs_name

    @property
    def libs_init_file_path(self) -> Path:
        return Path(self.libs_directory / "__init__.py")

    @property
    def core_paths(self) -> List[Path]:
        return [self.root, self.main_file_path, self.libs_directory, self.libs_init_file_path]


class ChallengeFolder:
    def __init__(self, name: str, parent: Path, main_file_name: str = CHALLENGE_MAIN_FILE_NAME,
                 libs_name: str = CHALLENGE_LIBS_NAME):
        self._challenge_structure = ChallengeStructure(_name=name, _parent=parent, _main_file_name=main_file_name,
                                                       _libs_name=libs_name)

    @staticmethod
    def _check_path_exists(path: Path) -> bool:
        exists = path.exists()
        logger.info(f"{path} doesn't exist.")
        return exists

    @staticmethod
    def _make(path: Path) -> None:
        path.touch(exist_ok=True) if path.suffix else path.mkdir(parents=True, exist_ok=True)
        logger.info(f"{path} made.") # todo : dont't log this if file already exists

    def exists(self) -> bool:
        return all([self._check_path_exists(path) for path in self._challenge_structure.core_paths])

    def mkdir(self) -> None:
        [self._make(path) for path in self._challenge_structure.core_paths]
