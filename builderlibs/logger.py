from pathlib import Path
import logging
from logging.config import dictConfig

import yaml


def logging_config_from_yaml(path: Path) -> dict:
    with open(path, 'r') as f:
        return yaml.safe_load(f.read())


class Logger:
    def __init__(self, conf_file_path: Path, name: str = "builder"):
        config = logging_config_from_yaml(conf_file_path)
        dictConfig(config)
        self._logger = logging.getLogger(name=name)

    def get(self):
        return self._logger
