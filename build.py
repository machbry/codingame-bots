import argparse
from pathlib import Path
from typing import Set, List
import ast

from builderlibs.directory_scanner import DirectoryScanner

BOT_FILE_NAME = "bot.py"
PROJECT_DIRECTORY = Path(__file__).parent.resolve()
BUILT_BOTS_DIRECTORY = "built_bots"
BUILT_BOTS_PATH = PROJECT_DIRECTORY / BUILT_BOTS_DIRECTORY


def get_imported_modules(file_path: Path) -> Set[str]:
    modules = []
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module)
    return set(modules)


def files_related_to_modules_in_directories(modules: Set[str], look_in_directories: List[Path]) -> Set[Path]:
    files = []
    for module in modules:
        for directory in look_in_directories:
            module_path = directory / (module.replace('.', '\\') + ".py")
            if module_path.is_file():
                files.append(module_path)
    return set(files)


parser = argparse.ArgumentParser()
parser.add_argument("-c", "--challenge_name", type=str)
parser.add_argument("-b", "--bot_file_name", type=str, default=BOT_FILE_NAME)
arguments = parser.parse_args().__dict__
challenge_name = arguments["challenge_name"]
bot_file_name = arguments["bot_file_name"]

directory_scanner = DirectoryScanner()
challenge_path, bot_file_path = directory_scanner.get_challenge_paths(challenge_name, bot_file_name)
bot_modules = get_imported_modules(bot_file_path)
print(bot_modules)

look_in_dirs = [PROJECT_DIRECTORY, challenge_path]
local_files_to_merge = files_related_to_modules_in_directories(bot_modules, look_in_dirs)
print(local_files_to_merge)

# with open('destination.py', 'w') as destination:
#     file_list = glob.glob('bots/*.py')
#     print(file_list)
#
#     dependencies = []
#     for file in file_list:
#         with open(file, 'r') as f:
#             tree = ast.parse(f.read())
#             for node in ast.walk(tree):
#                 if isinstance(node, ast.Import):
#                     dependencies.extend([n.name for n in node.names])
#                     # print(ast.dump(node))
#                 elif isinstance(node, ast.ImportFrom):
#                     dependencies.append(node.module)
#                     # print(ast.dump(node))
#
#     dependencies = sorted(set(dependencies))
#     # print(dependencies)
#
#     for dependency in dependencies:
#         destination.write(f'import {dependency}\n')
#
#     for file in file_list:
#         with open(file, 'r') as f:
#             destination.write(f.read())
