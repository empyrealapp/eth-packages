import os

from setuptools import find_packages, setup


def get_version():
    return os.getenv("PACKAGE_VERSION", "0.0.0")


setup(
    name="eth-rpc-py",
    version=get_version(),
)
