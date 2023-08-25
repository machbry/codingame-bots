from typing import Union, Literal
from os import PathLike
from pathlib import Path
from shutil import rmtree

from .logger import Logger


logger = Logger().get()


def log_node_event(on_path_exists: bool):
    def _log_node_event(node_method):
        def arguments_wrapper(*args, **kwargs):
            path: Path = args[0].path
            exists = path.exists()
            node_method(*args, **kwargs)
            if on_path_exists == exists:
                logger.info(f"Method \"{node_method.__name__}\" used on node at path \"{path}\".")
        return arguments_wrapper
    return _log_node_event


class Node:
    def __init__(self, path: Union[Path, str, PathLike]):
        self.path = Path(path).resolve()

    def exists(self) -> bool:
        return self.path.exists()

    def make(self) -> None:
        pass

    def destroy(self) -> None:
        pass


class Directory(Node):
    def __init__(self, path):
        super().__init__(path=path)
        self.path = self.path.parent / self.path.stem

    @log_node_event(on_path_exists=False)
    def make(self, mode=0o777, parents=True, exist_ok=True):
        self.path.mkdir(mode=mode, parents=parents, exist_ok=exist_ok)

    @log_node_event(on_path_exists=True)
    def destroy(self, ignore_errors=True, onerror=None):
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

    @log_node_event(on_path_exists=False)
    def make(self, mode=0o666, exist_ok=True):
        self.path.touch(mode=mode, exist_ok=exist_ok)

    @log_node_event(on_path_exists=True)
    def destroy(self, missing_ok=True):
        self.path.unlink(missing_ok=missing_ok)


class PythonFile(File):
    def __init__(self, path: Path):
        super().__init__(path=path, suffix='.py')
