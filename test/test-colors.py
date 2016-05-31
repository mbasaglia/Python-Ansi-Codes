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
import test_common

from patsi.document import palette
from patsi.document.color import *


class TestPalette(test_common.TestCase):
    names = ["foo", "bar"]
    colors = [(0xf, 0, 0), (0xb, 0xa, 2)]
    zipped = list(zip(names, colors))

    def test_ctor(self):
        p = palette.Palette(self.zipped)
        self.assertEqual(p.names, self.names)
        self.assertEqual(p.colors, self.colors)

        p = palette.Palette(*self.zipped)
        self.assertEqual(p.names, self.names)
        self.assertEqual(p.colors, self.colors)

        p = palette.Palette(item for item in self.zipped)
        self.assertEqual(p.names, self.names)
        self.assertEqual(p.colors, self.colors)

    def test_rgb(self):
        p = palette.Palette(self.zipped)
        self.assertEqual(p.rgb(0), self.colors[0])
        self.assertEqual(p.rgb(1), self.colors[1])
        self.assertRaises(IndexError, p.rgb, len(self.colors))

    def test_name(self):
        p = palette.Palette(self.zipped)
        self.assertEqual(p.name(0), self.names[0])
        self.assertEqual(p.name(1), self.names[1])
        self.assertRaises(IndexError, p.rgb, len(self.names))

    def test_iter(self):
        self.assertEqual(list(palette.Palette(self.zipped)), self.zipped)

    def test_add(self):
        other_names = ["fu", "ba", "foo"]
        other_colors = [(1,2,3), (3,4,5), (4,5,6)]
        other = palette.Palette(zip(other_names, other_colors))

        p = palette.Palette(self.zipped)
        p += other
        self.assertEqual(p.names, ["foo", "bar", "fu", "ba"])
        self.assertEqual(p.colors, [(4,5,6), (0xb, 0xa, 2), (1,2,3), (3,4,5)])

        q = palette.Palette(self.zipped)
        r = q + other
        self.assertEqual(list(q), self.zipped)
        self.assertEqual(list(r), list(p))

    def test_len(self):
        p = palette.Palette(self.zipped)
        self.assertEqual(len(p), len(self.colors))

    def test_builtin(self):
        self.assertEqual(len(palette.colors8_dark), 8)
        self.assertEqual(len(palette.colors8_bright), 8)
        self.assertEqual(len(palette.colors16), 16)
        self.assertEqual(len(palette.colors256), 256)

    def test_find_index(self):
        p = palette.Palette(self.zipped)
        self.assertEqual(p.find_index("bar"), 1)
        self.assertEqual(p.find_index(self.colors[1]), 1)

        self.assertRaises(Exception, p.find_index, "barr")


class TestIndexedColor(test_common.TestCase):
    def test_ctor(self):
        c = IndexedColor(2, palette.colors8_dark)
        self.assertEqual(c.index, 2)
        self.assertIs(c.palette, palette.colors8_dark)

        c = IndexedColor("blue", palette.colors8_dark)
        self.assertEqual(c.index, 4)
        self.assertIs(c.palette, palette.colors8_dark)

    def test_rgb(self):
        color = IndexedColor(2, palette.colors8_dark)
        self.assertIs(type(color.rgb), RgbColor)
        self.assertEqual(color.rgb, palette.colors8_dark.rgb(2))

    def test_rgb_tuple(self):
        color = IndexedColor(2, palette.colors8_dark)
        self.assertIs(type(color.rgb_tuple), tuple)
        self.assertEqual(color.rgb_tuple, palette.colors8_dark.rgb_tuple(2))

    def test_name(self):
        self.assertEqual(
            IndexedColor(2, palette.colors8_dark).name,
            palette.colors8_dark.name(2)
        )

    def test_cmp(self):
        a = IndexedColor(2, palette.colors8_bright)
        b = IndexedColor(2, palette.colors8_bright)
        c = IndexedColor(3, palette.colors8_bright)
        d = IndexedColor(2, palette.colors8_dark)
        e = IndexedColor(10, palette.colors16)

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

        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))
        self.assertNotEqual(hash(a), hash(d))
        self.assertNotEqual(hash(a), hash(None))
        self.assertNotEqual(hash(a), hash(e)) # Should this result equal?


class TestRgbColor(test_common.TestCase):
    def test_hex_rgb(self):
        self.assertEqual(RgbColor(0xf1, 0x2, 0x34).hex(), "#f10234")

    def test_ctor(self):
        c = RgbColor(1, 2, 3)
        self.assertEqual(c.r, 1)
        self.assertEqual(c.g, 2)
        self.assertEqual(c.b, 3)

    def test_rgb(self):
        c = RgbColor(1, 2, 3)
        self.assertIs(type(c.rgb), RgbColor)
        self.assertEqual(c.rgb, c)

    def test_rgb_tuple(self):
        c = RgbColor(1, 2, 3)
        self.assertIs(type(c.rgb_tuple), tuple)
        self.assertEqual(c.rgb_tuple, (1, 2, 3))

    def test_name(self):
        c = RgbColor(1, 2, 3)
        self.assertEqual(c.name, c.hex())
        c.name = "foocolor"
        self.assertEqual(c.name, "foocolor")
        del c.name
        self.assertEqual(c.name, c.hex())

    def test_cmp(self):
        a = RgbColor(1, 2, 3)
        b = RgbColor(1, 2, 3, "foocolor")
        c = RgbColor(9, 2, 3)
        d = RgbColor(1, 9, 3)
        e = RgbColor(1, 2, 9)
        p = palette.Palette(
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

        self.assertEqual(hash(a), hash(b))
        self.assertNotEqual(hash(a), hash(c))
        self.assertNotEqual(hash(a), hash(d))
        self.assertNotEqual(hash(a), hash(e))
        self.assertNotEqual(hash(a), hash(f)) # Should be equal?
        self.assertNotEqual(hash(a), hash(g))
        self.assertNotEqual(hash(a), hash(None))

    def test_copy(self):
        color = RgbColor(1, 2, 3, "foocolor")
        copy = color.copy()
        self.assertEqual(color, copy)
        self.assertEqual(color.name, copy.name)
        self.assertIsNot(color, copy)


test_common.main()
