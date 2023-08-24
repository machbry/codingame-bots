from unittest.mock import Mock, patch

import pytest

from builderlibs.fileutils import Directory, File


@pytest.mark.parametrize("dirname", [
    "dirname",
    "dirname.py",
    None])
def test_directory(data_tests_path, dirname):
    path = data_tests_path / dirname if dirname is not None else ""
    directory = Directory(path)
    assert not directory.path.suffix


@pytest.mark.parametrize("mode, parents, exist_ok", [
    (0o777, True, True),
    (0, False, False)
])
def test_directory_make(data_tests_path, mode, parents, exist_ok):
    directory = Directory(data_tests_path / "dirname")
    directory.path = Mock()

    directory.make(mode=mode, parents=parents, exist_ok=exist_ok)

    directory.path.mkdir.assert_called_with(mode=mode, parents=parents, exist_ok=exist_ok)


@pytest.mark.parametrize("ignore_errors, onerror", [
    (False, None),
    (True, None)
])
def test_directory_destroy(data_tests_path, ignore_errors, onerror):
    with patch("builderlibs.fileutils.rmtree") as mock_rmtree:
        directory = Directory(data_tests_path / "dirname")

        directory.destroy(ignore_errors=ignore_errors, onerror=onerror)

        mock_rmtree.assert_called_with(directory.path, ignore_errors=ignore_errors, onerror=onerror)


@pytest.mark.parametrize("name, suffix, result_stem, result_suffix", [
    ("readme", ".md", "readme", ".md"),
    ("readme", "md", "readme", ".md"),
    ("document.txt", ".json", "document", ".json"),
    ("document", ".txt.md", "document.txt", ".md"),
    ("main.py", "", None, None)])
def test_file(data_tests_path, name, suffix, result_stem, result_suffix):
    path = data_tests_path / name
    if suffix == "":
        with pytest.raises(ValueError):
            File(path, suffix)
    else:
        file = File(path, suffix)
        assert file.path.parent == data_tests_path
        assert file.path.stem == result_stem
        assert file.path.suffix == result_suffix


@pytest.mark.parametrize("mode, exist_ok", [
    (0o777, True),
    (0, False)
])
def test_file_make(data_tests_path, mode, exist_ok):
    file = File(data_tests_path / "filename", suffix=".txt")
    file.path = Mock()

    file.make(mode=mode, exist_ok=exist_ok)

    file.path.touch.assert_called_with(mode=mode, exist_ok=exist_ok)


@pytest.mark.parametrize("missing_ok", [
    False,
    True
])
def test_file_destroy(data_tests_path, missing_ok):
    file = File(data_tests_path / "filename", suffix=".txt")
    file.path = Mock()

    file.destroy(missing_ok=missing_ok)

    file.path.unlink.assert_called_with(missing_ok=missing_ok)
