from unittest.mock import patch

import pytest

from builderlibs.fileutils import Directory, PythonFile
from builderlibs.challenge import ChallengeStructure, ChallengeFolder
from tests.constants import TESTS_DATA_PATH


@pytest.mark.parametrize("name, parent, main_file_name, libs_name", [
    ("challenge_structure_test", TESTS_DATA_PATH, "bot", "challengelibs"),
    ("", TESTS_DATA_PATH, "bot", "challengelibs"),
    (None, TESTS_DATA_PATH, "bot", "challengelibs")])
def test_challenge_structure(name, parent, main_file_name, libs_name):
    if name in ["", None]:
        with pytest.raises(ValueError):
            ChallengeStructure(_name=name,
                               _parent=parent,
                               _main_file_name=main_file_name,
                               _libs_name=libs_name)
    else:
        challenge_structure = ChallengeStructure(_name=name,
                                                 _parent=parent,
                                                 _main_file_name=main_file_name,
                                                 _libs_name=libs_name)

        root = challenge_structure.root
        main_file = challenge_structure.main_file
        libs = challenge_structure.libs
        libs_init_file = challenge_structure.libs_init_file

        assert isinstance(root, Directory)
        assert isinstance(main_file, PythonFile)
        assert isinstance(libs, Directory)
        assert isinstance(libs_init_file, PythonFile)

        assert main_file.path.parent == root.path
        assert libs.path.parent == root.path
        assert libs_init_file.path.parent == libs.path


@pytest.mark.parametrize("force_destroy, user_input", [
    (True, None),
    (False, "Y"),
    (False, "n")
])
def test_challenge_folder(force_destroy, user_input):
    challenge_folder = ChallengeFolder(name="test_challenge_folder", parent=TESTS_DATA_PATH)

    with patch("builtins.input") as mock_input:
        mock_input.return_value = user_input

        assert not challenge_folder.exists()

        challenge_folder.make()
        assert challenge_folder.exists()

        challenge_folder.destroy(force_destroy=force_destroy)
        assert (not challenge_folder.exists()) == (force_destroy or user_input == "Y")

        # clean after
        if challenge_folder.exists():
            challenge_folder.destroy(force_destroy=True)
