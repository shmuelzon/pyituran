"""Python setup.py for pyituran package"""
import io
import os
from setuptools import find_packages, setup


REPO_URL = "https://github.com/shmuelzon/pyituran"
VERSION = os.environ["VERSION"]

def read(*paths, **kwargs):
    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="pyituran",
    version=VERSION,
    description="A module to interact with Ituran's web service.",
    url=REPO_URL,
    download_url=REPO_URL + "/tarball/" + VERSION,
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Shmuelzon",
    packages=find_packages(include=["pyituran*"]),
    install_requires=read_requirements("requirements.txt"),
    extras_require={"test": read_requirements("dev-requirements.txt")},
    python_requires=">=3.8",
    license="MIT",
    entry_points={"console_scripts": ["ituran = pyituran.cmdline:main"]},
)
