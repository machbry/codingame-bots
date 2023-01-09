import os
from pathlib import Path
from typing import List, Dict

ABSPATH = Path(__file__).parent.parent.resolve()
DIRECTORY_PATH = os.path.join(ABSPATH, "bots")


class DirectoryScanner:
    def __init__(self):
        self._challenges_names: List[str] = os.listdir(DIRECTORY_PATH)
        self.challenges_paths: Dict[str, str] = {challenge_name: Path(os.path.join(DIRECTORY_PATH, challenge_name)).resolve() \
                                                  for challenge_name in self._challenges_names}

    @property
    def challenges_names(self) -> List[str]:
        return self._challenges_names

    def get_challenge_path(self, challenge_name: str) -> str:
        challenge_path = self.challenges_paths.get(challenge_name)
        if challenge_path is None:
            raise Exception(f"Challenge {challenge_name} not found. Known challenges are : {self._challenges_names}.")
        return challenge_path

    def get_bot_file_path(self, challenge_name: str, bot_file_name: str) -> str:
        challenge_path = self.get_challenge_path(challenge_name)
        bot_file_path = Path(os.path.join(challenge_path, bot_file_name)).resolve()
        if not os.path.isfile(bot_file_path):
            raise FileNotFoundError(f"File {bot_file_name} not found in challenge directory {challenge_path}.")
        return bot_file_path
