from pathlib import Path

import pytest


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
def unbuilt_bots_parent() -> Path:
    return TESTS_ROOT_PATH / "res" / "bots"
