import os
from pathlib import Path
from typing import List, Dict

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

    def get_challenge_path(self, challenge_name: str) -> Path:
        challenge_path = self.challenges_paths.get(challenge_name)
        if challenge_path is None:
            raise Exception(f"Challenge {challenge_name} not found. Known challenges are : {self._challenges_names}.")
        return challenge_path

    def get_bot_file_path(self, challenge_name: str, bot_file_name: str) -> Path:
        challenge_path = self.get_challenge_path(challenge_name)
        bot_file_path = challenge_path / bot_file_name
        if not bot_file_path.is_file():
            raise FileNotFoundError(f"File {bot_file_name} not found in challenge directory {challenge_path}.")
        return bot_file_path
