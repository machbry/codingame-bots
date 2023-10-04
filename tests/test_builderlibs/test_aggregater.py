import pytest

from builderlibs.aggregater import LocalModuleImportReplacer
from constants import TESTS_RES_PATH


@pytest.fixture
def local_module_import_replacer(test_challenge):
    local_packages_paths = [TESTS_RES_PATH / "sharelibs"]
    main_module = test_challenge.main_module
    return LocalModuleImportReplacer(main_module, local_packages_paths)


def test_replacer_visit_import(local_module_import_replacer, create_ast_import_node):
    import_node = create_ast_import_node("import challengelibs")
    with pytest.raises(ValueError):
        local_module_import_replacer.visit_Import(import_node)
