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
import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from patsi.document.tree import *


class TestDocument(unittest.TestCase):
    def test_layer(self):
        l = Layer()
        self.assertEquals(l.text, "")
        self.assertEquals(l.color, None)
        self.assertEquals(l.width, 0)
        self.assertEquals(l.height, 0)

        l = Layer("foo\nBar!\n")
        self.assertEquals(l.text, "foo\nBar!\n")
        self.assertEquals(l.color, None)
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)
        self.assertEquals(l.lines, ["foo", "Bar!"])
        self.assertEquals(l.lines[1][3], "!")
        l.set_char(1, 0, "X")
        self.assertEquals(l.lines[0][1], "X")
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)
        l.set_char(5, 5, "X")
        self.assertEquals(l.lines[5][5], "X")
        self.assertEquals(l.width, 6)
        self.assertEquals(l.height, 6)

        l = Layer("foo\nBar!\n\n")
        self.assertEquals(l.text, "foo\nBar!\n\n")
        self.assertEquals(l.height, 3)
        self.assertEquals(l.lines, ["foo", "Bar!", ""])

        l = Layer("foo\nBar!")
        self.assertEquals(l.text, "foo\nBar!\n")
        self.assertEquals(l.color, None)
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)
        self.assertEquals(l.lines, ["foo", "Bar!"])

        l = Layer("foo\nBar!\n", RgbColor(1, 2, 3))
        self.assertEquals(l.text, "foo\nBar!\n")
        self.assertEquals(l.color, RgbColor(1, 2, 3))
        self.assertEquals(l.width, 4)
        self.assertEquals(l.height, 2)

    def test_free_color_layer(self):
        l = FreeColorLayer()
        self.assertFalse(l.matrix)
        self.assertEquals(l.width, 0)
        self.assertEquals(l.height, 0)

        self.assertFalse((4, 5) in l.matrix)
        l.set_char(4, 5, "x", RgbColor(1, 2, 3))
        self.assertTrue((4, 5) in l.matrix)
        self.assertEquals(l.matrix[(4, 5)], ("x", RgbColor(1, 2, 3)))
        self.assertEquals(l.width, 5)
        self.assertEquals(l.height, 6)

        l.set_char(4, 5, "y", RgbColor(3, 2, 1))
        self.assertEquals(l.matrix[(4, 5)], ("y", RgbColor(3, 2, 1)))
        self.assertEquals(l.width, 5)
        self.assertEquals(l.height, 6)

        l.set_char(1, 1, "y")
        self.assertEquals(l.matrix[(1, 1)], ("y", None))
        self.assertEquals(l.width, 5)
        self.assertEquals(l.height, 6)

        # TODO Test add_layer

    def test_document(self):
        pass
        # TODO

#TODO Test formatters

unittest.main()
