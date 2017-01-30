#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
from io import open
import os.path
from setuptools import setup


def read_file(filename):
    full_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), filename)
    with open(full_path, "rt", encoding="utf-8") as f:
        lines = f.readlines()
    return lines


def get_version():
    pattern = re.compile(r"__version__ = \"(?P<version>[0-9.a-zA-Z-]+)\"")
    for line in read_file(os.path.join("mlalchemy", "__init__.py")):
        m = pattern.match(line)
        if m is not None:
            return m.group('version')
    raise ValueError("Cannot extract version number for MLAlchemy")


setup(
    name="mlalchemy",
    version=get_version(),
    description="Library for converting YAML/JSON to SQLAlchemy SELECT queries",
    long_description="".join(read_file("README.rst")),
    author="Thane Thomson",
    author_email="connect@thanethomson.com",
    url="https://github.com/thanethomson/MLAlchemy",
    install_requires=[r.strip() for r in read_file("requirements.txt") if len(r.strip()) > 0],
    license='MIT',
    packages=["mlalchemy"],
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: MacOS",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Database",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries"
    ]
)
