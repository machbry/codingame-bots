from typing import Union
from os import PathLike
from pathlib import Path
from shutil import rmtree


class Node:
    def __init__(self, path: Union[Path, str, PathLike]):
        self.path = Path(path).resolve()

    def make(self) -> None:
        pass

    def destroy(self) -> None:
        pass


class Directory(Node):
    def __init__(self, path):
        super().__init__(path=path)
        self.path = self.path.parent / self.path.stem

    def make(self, mode=0o777, parents=False, exist_ok=False):
        self.path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    def destroy(self, ignore_errors=False, onerror=None):
        rmtree(self.path, ignore_errors=ignore_errors, onerror=onerror)


class File(Node):
    def __init__(self, path, suffix: str):
        super().__init__(path=path)

        if suffix == "":
            raise ValueError("suffix given can't be empty")

        if not suffix.startswith("."):
            suffix = "." + suffix

        if path.suffix != suffix:
            self.path = self.path.parent / (self.path.stem + suffix)

    def make(self, mode=0o666, exist_ok=True):
        self.path.touch(mode=mode, exist_ok=exist_ok)

    def destroy(self, missing_ok=False):
        self.path.unlink(missing_ok=missing_ok)


class PythonFile(File):
    def __init__(self, path: Path):
        super().__init__(path=path, suffix='.py')
