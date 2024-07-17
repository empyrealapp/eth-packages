from setuptools import find_packages, setup

setup(
    name="eth-packages",
    version="0.1.1",
    packages=find_packages(
        include=[
            "packages/eth_rpc*",
            "packages/eth_typeshed*",
        ]
    ),
    # Other setup arguments
)
