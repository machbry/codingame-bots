from setuptools import setup, find_packages, find_namespace_packages

setup(
    name="codingame_bots",
    version="0.1",
    packages=find_packages(),
    package_data={'builderlibs': ['conf/*.yaml']}
)
