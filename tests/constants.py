from pathlib import Path


TESTS_ROOT_PATH = Path(__file__).parent.resolve()
TESTS_DATA_PATH = TESTS_ROOT_PATH / "data"
TESTS_RES_PATH = TESTS_ROOT_PATH / "res"
TESTS_BOTS_PATH = TESTS_RES_PATH / "bots"
TESTS_BOTLIBS_PATH = TESTS_RES_PATH / "botlibs"
TESTS_SHAREDLIBS_PATH = TESTS_RES_PATH / "sharedlibs"

TESTS_DATA_PATH.mkdir(exist_ok=True, parents=True)
