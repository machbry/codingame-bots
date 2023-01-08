from pathlib import Path
import ast
import glob

from builderlibs.directory_scanner import DirectoryScanner

ABSPATH = Path(__file__).parent.resolve()
CHALLENGE_NAME = "death_first_search_ep1"
BOT_FILE_NAME = "bot.py"

directory_scanner = DirectoryScanner()
challenge_path = directory_scanner.get_challenge_path(CHALLENGE_NAME)
bot_file_path = directory_scanner.get_bot_file_path(CHALLENGE_NAME, BOT_FILE_NAME)


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
