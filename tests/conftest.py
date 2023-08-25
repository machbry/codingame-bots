from pathlib import Path

import pytest

from builderlibs.challenge import ChallengeFolder


TESTS_ROOT_PATH = Path(__file__).parent.resolve()


def make_dir(function_returning_path):
    def make_dir_wrapper(*args, **kwargs):
        path: Path = function_returning_path(*args, **kwargs)
        path.mkdir(exist_ok=True, parents=True)
        return path
    return make_dir_wrapper


@pytest.fixture(scope="session")
@make_dir
def data_tests_path() -> Path:
    return TESTS_ROOT_PATH / "data"


@pytest.fixture(scope="session")
@make_dir
def res_tests_path() -> Path:
    return TESTS_ROOT_PATH / "res"


@pytest.fixture(scope="session")
@make_dir
def unbuilt_bots_tests_parent() -> Path:
    return TESTS_ROOT_PATH / "res" / "bots"


@pytest.fixture(scope="session")
def create_challenge_folder(unbuilt_bots_tests_parent):

    folders_made = []

    def _create_challenge_folder(name: str, make: bool = False):
        challenge_folder = ChallengeFolder(name=name, parent=unbuilt_bots_tests_parent)
        if make:
            challenge_folder.make()
            folders_made.append(challenge_folder)
        return challenge_folder

    yield _create_challenge_folder

    [folder.destroy() for folder in folders_made]