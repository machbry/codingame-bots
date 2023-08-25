import pytest

from builderlibs.fileutils import Directory, PythonFile
from builderlibs.challenge import ChallengeStructure, ChallengeFolder


@pytest.mark.parametrize("name, parent, main_file_name, libs_name", [
    ("challenge_structure_test", "unbuilt_bots_tests_parent", "bot", "challengelibs")])
def test_challenge_structure(name, parent, main_file_name, libs_name, request):
    challenge_structure = ChallengeStructure(_name=name,
                                             _parent=request.getfixturevalue(parent),
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


def test_challenge_folder(unbuilt_bots_tests_parent):
    challenge_folder = ChallengeFolder(name="test_challenge_folder", parent=unbuilt_bots_tests_parent)

    assert not challenge_folder.exists()
    challenge_folder.make()
    assert challenge_folder.exists()
    challenge_folder.destroy()
    assert not challenge_folder.exists()
