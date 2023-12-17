import pytest

from builderlibs.aggregater import LocalModuleReplacer
from constants import TESTS_RES_PATH, TESTS_SHAREDLIBS_PATH, TESTS_DATA_PATH


@pytest.fixture
def local_module_replacer(test_challenge):
    local_packages_paths = [TESTS_RES_PATH / "sharedlibs"]
    main_module = test_challenge.main_module
    return LocalModuleReplacer(main_module, local_packages_paths)


@pytest.mark.parametrize("import_statement, exception_expected", [
    ("import challengelibs", ValueError),
    ("import sharedlibs", ValueError),
    ("import pandas as pd", None)
])
def test_replacer_visit_import(import_statement, exception_expected, local_module_replacer,
                               create_ast_imports_nodes):
    import_node = create_ast_imports_nodes(import_statement)[0]
    if exception_expected:
        with pytest.raises(ValueError):
            local_module_replacer.visit_Import(import_node)
    else:
        assert import_node == local_module_replacer.visit_Import(import_node)


@pytest.mark.skip("Test is not implemented")
@pytest.mark.parametrize("import_statement, node_expected", [
    ("from challengelibs import module", None)
])
def test_replacer_visit_import_from(import_statement, node_expected, local_module_replacer,
                                    create_ast_imports_nodes):
    import_from_node = create_ast_imports_nodes(import_statement)[0]
    # TODO : test LocalModuleReplacer.visit_ImportFrom()


def test_challenge_build(test_challenge):
    challenge_source = test_challenge.aggregate_to_source(local_packages_paths=[TESTS_SHAREDLIBS_PATH])
    with open(TESTS_DATA_PATH / (test_challenge.name + ".py"), "w") as f:
        f.write(challenge_source)
