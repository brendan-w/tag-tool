#!/bin/env python
# -*- coding: utf8 -*-

from setuptools import setup, find_packages

setup(
    name="tagtool",
    version="0.0.1",
    description=("CLI for altering filenames in a tag-based fashion"),
    classifiers=[
        "Operating System :: POSIX :: Linux",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Programming Language :: Python :: 3",
        "Development Status :: 3 - Alpha"
    ],
    keywords="file tag tagging rename",
    author="Brendan Whitfield",
    author_email="brendanw@windworksdesign.com",
    url="http://github.com/brendan-w/tag-tool",
    license="GNU GPLv2",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    scripts=[
        'bin/tag',
        'bin/tag-find',
        'bin/tag-list',
        'bin/tag-organize',
        'bin/tag-dialog',
    ],
)
