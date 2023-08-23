import os
from pathlib import Path
from typing import List, Dict, Tuple

ABSPATH = Path(__file__).parent.parent.resolve()
BOTS_PATH = ABSPATH / "bots"


class DirectoryScanner:
    def __init__(self):
        self._challenges_names: List[str] = os.listdir(BOTS_PATH)
        self.challenges_paths: Dict[str, Path] = {
            challenge_name: BOTS_PATH / challenge_name for challenge_name in self._challenges_names}

    @property
    def challenges_names(self) -> List[str]:
        return self._challenges_names

    def get_challenge_paths(self, challenge_name: str, bot_file_name: str, challenge_libs_name: str) -> Tuple[Path, Path, Path]:
        challenge_path = self.challenges_paths.get(challenge_name)
        if challenge_path is None:
            raise Exception(f"Challenge {challenge_name} not found. Known challenges are : {self._challenges_names}.")
        bot_file_path = challenge_path / bot_file_name
        if not bot_file_path.is_file():
            raise FileNotFoundError(f"File {bot_file_name} not found in challenge directory {challenge_path}.")
        challenge_libs_path = challenge_path / challenge_libs_name
        if not challenge_libs_path.is_dir():
            raise FileNotFoundError(f"Directory {challenge_libs_name} not found in challenge directory {challenge_path}.")
        return challenge_path, bot_file_path, challenge_libs_path
