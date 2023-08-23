from setuptools import setup, find_packages

setup(
    name="codingame_bots",
    version="0.1",
    package_dir={"botlibs": "botlibs",
                 "builderlibs": "builderlibs"},
    packages=["botlibs", "builderlibs"]
)
