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

class TestPalette(unittest.TestCase):
    names = ["foo", "bar"]
    colors = [(0xf, 0, 0), (0xb, 0xa, 2)]
    zipped = zip(names, colors)

    def test_ctor(self):
        p = Palette(self.zipped)
        self.assertEquals(p.names, self.names)
        self.assertEquals(p.colors, self.colors)

        p = Palette(*self.zipped)
        self.assertEquals(p.names, self.names)
        self.assertEquals(p.colors, self.colors)

        p = Palette(item for item in self.zipped)
        self.assertEquals(p.names, self.names)
        self.assertEquals(p.colors, self.colors)

    def test_rgb(self):
        p = Palette(self.zipped)
        self.assertEquals(p.rgb(0), self.colors[0])
        self.assertEquals(p.rgb(1), self.colors[1])
        self.assertRaises(IndexError, p.rgb, len(self.colors))

    def test_name(self):
        p = Palette(self.zipped)
        self.assertEquals(p.name(0), self.names[0])
        self.assertEquals(p.name(1), self.names[1])
        self.assertRaises(IndexError, p.rgb, len(self.names))

    def test_iter(self):
        self.assertEquals(list(Palette(self.zipped)), self.zipped)

    def test_add(self):
        other_names = ["fu", "ba", "foo"]
        other_colors = [(1,2,3), (3,4,5), (4,5,6)]
        other = Palette(zip(other_names, other_colors))

        p = Palette(self.zipped)
        p += other
        self.assertEquals(p.names, ["foo", "bar", "fu", "ba"])
        self.assertEquals(p.colors, [(4,5,6), (0xb, 0xa, 2), (1,2,3), (3,4,5)])

        q = Palette(self.zipped)
        r = q + other
        self.assertEquals(list(q), self.zipped)
        self.assertEquals(list(r), list(p))

    def test_len(self):
        p = Palette(self.zipped)
        self.assertEquals(len(p), len(self.colors))

    def test_builtin(self):
        self.assertEquals(len(colors8_dark), 8)
        self.assertEquals(len(colors8_bright), 8)
        self.assertEquals(len(colors16), 16)
        # self.assertEquals(len(colors256), 256) TODO

    def test_find_index(self):
        p = Palette(self.zipped)
        self.assertEquals(p.find_index("bar"), 1)
        self.assertEquals(p.find_index(self.colors[1]), 1)

        self.assertRaises(Exception, p.find_index, "barr")


class TestIndexedColor(unittest.TestCase):
    def test_ctor(self):
        c = IndexedColor(2, colors8_dark)
        self.assertEquals(c.index, 2)
        self.assertIs(c.palette, colors8_dark)

        c = IndexedColor("blue", colors8_dark)
        self.assertEquals(c.index, 4)
        self.assertIs(c.palette, colors8_dark)

    def test_rgb(self):
        self.assertEquals(
            IndexedColor(2, colors8_dark).rgb,
            colors8_dark.rgb(2)
        )

    def test_name(self):
        self.assertEquals(
            IndexedColor(2, colors8_dark).name,
            colors8_dark.name(2)
        )

    def test_cmp(self):
        a = IndexedColor(2, colors8_bright)
        b = IndexedColor(2, colors8_bright)
        c = IndexedColor(3, colors8_bright)
        d = IndexedColor(2, colors8_dark)
        e = IndexedColor(10, colors16)

        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(a == None)
        self.assertTrue(a == e)

        self.assertFalse(a != b)
        self.assertTrue(a != c)
        self.assertTrue(a != d)
        self.assertFalse(a != e)
        self.assertTrue(a != None)


class TestRgbColor(unittest.TestCase):
    def test_helpers(self):
        self.assertEquals(hex_rgb((0xf1, 0x2, 0x34)), "#f10234")

    def test_ctor(self):
        c = RgbColor(1, 2, 3)
        self.assertEquals(c.r, 1)
        self.assertEquals(c.g, 2)
        self.assertEquals(c.b, 3)

    def test_rgb(self):
        c = RgbColor(1, 2, 3)
        self.assertEquals(c.rgb, (1, 2, 3))

    def test_name(self):
        c = RgbColor(1, 2, 3)
        self.assertEquals(c.name, hex_rgb(c.rgb))

        c = RgbColor(1, 2, 3, "foocolor")
        self.assertEquals(c.name, "foocolor")

    def test_cmp(self):
        a = RgbColor(1, 2, 3)
        b = RgbColor(1, 2, 3, "foocolor")
        c = RgbColor(9, 2, 3)
        d = RgbColor(1, 9, 3)
        e = RgbColor(1, 2, 9)
        p = Palette(
            ("a", (1,2,3)),
            ("b", (3,2,1)),
        )
        f = IndexedColor(0, p)
        g = IndexedColor(1, p)

        self.assertTrue(a == b)
        self.assertFalse(a == c)
        self.assertFalse(a == d)
        self.assertFalse(a == e)
        self.assertTrue(a == f)
        self.assertFalse(a == g)
        self.assertFalse(a == None)

        self.assertFalse(a != b)
        self.assertTrue(a != c)
        self.assertTrue(a != d)
        self.assertTrue(a != e)
        self.assertFalse(a != f)
        self.assertTrue(a != g)
        self.assertTrue(a != None)


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
