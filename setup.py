from setuptools import find_packages, setup

setup(
    name="eth-packages",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    packages=find_packages(
        include=[
            "packages/eth_rpc*",
            "packages/eth_typeshed*",
        ]
    ),
    # Other setup arguments
)
