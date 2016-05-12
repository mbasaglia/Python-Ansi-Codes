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
from StringIO import StringIO


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
            "".join(repr(arg) for arg in args)
        )


def main():
    if inspect.getmodule(inspect.stack()[1][0]).__name__ == "__main__":
        unittest.main()
