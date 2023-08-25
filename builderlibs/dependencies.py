from pathlib import Path
from typing import List
import ast


def get_imported_modules(file_path: Path) -> List[str]:
    modules = []
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend([n.name for n in node.names])
            elif isinstance(node, ast.ImportFrom):
                modules.append(node.module)
    return modules
