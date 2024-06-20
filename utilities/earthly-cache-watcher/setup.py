from setuptools import setup, find_packages

setup(
    name="earthly-cache-watcher",
    version="0.1.0",
    description="Earthly cache watcher",
    packages=find_packages(),
    install_requires=[
        "watchdog",
    ],
)