from dataclasses import dataclass
from pathlib import Path


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
