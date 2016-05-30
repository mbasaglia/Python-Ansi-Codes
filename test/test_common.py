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
import sys
import inspect
import unittest
from unittest import TestCase
from six import BytesIO as StringIO


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class StringOutputTestCase(unittest.TestCase):
    def setUp(self):
        self.output = StringIO()

    def _get_data(self):
        return self.output.getvalue()

    def _clear_data(self):
        self.output.truncate(0)
        self.output.seek(0)

    def _check_data(self, *args):
        self.assertEquals(
            self._get_data(),
            "".join(str(arg) for arg in args)
        )


class MockFile(object):
    def __init__(self, wrapped=StringIO()):
        self._wrapped = wrapped

    def __getattr__(self, name):
        if name != "_wrapped" and name not in vars(self):
            return getattr(self._wrapped, name)
        return super(MockFile, self).__getattr__(name)

    def __delattr__(self, name):
        if name != "_wrapped" and name not in vars(self):
            return delattr(self._wrapped, name)

    def __setattr__(self, name, value):
        if name != "_wrapped" and name not in vars(self):
            return setattr(self._wrapped, name, value)
        return super(MockFile, self).__setattr__(name, value)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def open(self, file, mode="r"):
        self.name = file
        self.mode = mode
        return self

    def reset(self, contents=""):
        self._wrapped = StringIO(contents)


def main():
    if inspect.getmodule(inspect.stack()[1][0]).__name__ == "__main__":
        unittest.main()
