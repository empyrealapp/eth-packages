import os

from setuptools import setup


def get_version():
    return os.getenv("PACKAGE_VERSION", "0.0.0")


setup(
    name="sapphire-py",
    version=get_version(),
)
