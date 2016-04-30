#!/usr/bin/env python
#
# Copyright (C) 2016 Mattia Basaglia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import os
from distutils.core import setup

def get_packages(root):
    if type(root) is str:
        root = [root]
    return sum((
        get_packages(root + [subdir])
        for subdir in
        os.listdir(os.path.join(*root))
        if os.path.isdir(os.path.join(*(root + [subdir])))
    ), [".".join(root)])


setup(
    name="patsi",
    version="0.2",
    description="Python ANSI Terminal Styling Interface",
    long_description="""A Python library to handle ANSI style codes and documents containing colored ASCII art.""",
    author="Mattia Basaglia",
    author_email="mattia.basaglia@gmail.com",
    url="https://github.com/mbasaglia/Python-Ansi-Terminal-Styling-Interface",
    packages=get_packages("patsi"),
    scripts=["patsi-render.py"],
    license="GPLv3+",
    platforms=["any"],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Terminals",
        "Operating System :: OS Independent",
    ],
)
