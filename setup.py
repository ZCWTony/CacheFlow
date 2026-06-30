from setuptools import setup, find_packages

setup(
    name="cacheflow",
    version="1.0.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "ryu==4.34",
        "networkx==2.8",
        "pyyaml==6.0",
    ],
    author="Zhao Chenwei",
    description="Dependency-aware rule caching for SDN",
    license="Apache 2.0",
)
