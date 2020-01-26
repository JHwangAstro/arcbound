""" Arcbound is a collection of tools used to develop and maintain data-driven
Python code, organizing attributes and methods of a class into a graph.
"""

import os
import re

from setuptools import setup, find_packages

__author__ = "Jason Hwang"
__email__ = "@".join(["jhwang.astro", "gmail.com"])
__url__ = "https://github.com/JHwangAstro/arcbound"
__description__ = "Collection of tools to arrange bound methods into a graph."

def get_version(*paths) -> str:
    """ Returns the version number by looking in the file paths specified.
    Assumes that the paths provided are relative.

    Args:
        paths: Relative path to the file containing the version.

    Raises:
        RuntimeError: If the version string is unable to be found.
    """
    setup_file_path = os.path.abspath(os.path.dirname(__file__))
    init_path = os.path.join(setup_file_path, *paths)

    with open(init_path) as init_file:
        init_blob = init_file.read()

    version_match = re.search(
        r"^__version__ = ['\"]([^'\"]*)['\"]",
        init_blob,
        re.M
    )

    if version_match is None:
        raise RuntimeError("Unable to find version string.")

    else:
        version = version_match.group(1)

    return version

this_directory = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

install_requires = [
    "attrs>=19.3.0"
]

extras_require = {
    # Required to visualize methods graph.
    "graphviz": ["graphviz==0.13.2"]
}

setup(
    name="arcbound",
    version=get_version("arcbound", "release.py"),
    description=__description__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    author_email=__email__,
    url=__url__,
    python_requires=">=3.6",
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent"
    ]
)

