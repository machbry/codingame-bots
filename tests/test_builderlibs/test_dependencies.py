import pytest

from builderlibs.challenge import ChallengeFolder
from builderlibs.dependencies import Module


@pytest.fixture(scope="session")
def dependencies_test_challenge(create_challenge_folder) -> ChallengeFolder:
    return create_challenge_folder(name="dependencies_test_challenge")


@pytest.mark.parametrize("module_name, imported_from, level, relative_path_expected, is_local_expected", [
    ("math", "main_file", 0, "math.py", False),
    ("os.path", "main_file", 0, "os/path.py", False),
    ("challengelibs.module", "main_file", 0, "challengelibs/module.py", True),
    ("other_module", "libs_init_file", 0, "other_module.py", True),
    ("pandas", "libs_init_file", 0, "pandas.py", False)
])
def test_module(module_name, imported_from, level, relative_path_expected, is_local_expected,
                dependencies_test_challenge):
    imported_from = getattr(dependencies_test_challenge.challenge_structure, imported_from).path
    module = Module(name=module_name)

    path_to_check = module._path_to_check(imported_from=imported_from, level=level)
    assert path_to_check == imported_from.parent / relative_path_expected

    is_local = module.is_local(imported_from=imported_from, level=level)
    assert is_local == is_local_expected
