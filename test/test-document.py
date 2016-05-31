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

from patsi.document.tree import *
from patsi.document import color
from patsi.document import _misc


class TestLayer(test_common.TestCase):
    def test_empty(self):
        l = Layer()
        self.assertEqual(l.text, "")
        self.assertEqual(l.color, None)
        self.assertEqual(l.width, 0)
        self.assertEqual(l.height, 0)

    def test_set_char(self):
        l = Layer("foo\nBar!\n")
        self.assertEqual(l.text, "foo\nBar!\n")
        self.assertEqual(l.color, None)
        self.assertEqual(l.width, 4)
        self.assertEqual(l.height, 2)
        self.assertEqual(l.lines, ["foo", "Bar!"])
        self.assertEqual(l.lines[1][3], "!")
        l.set_char(1, 0, "X")
        self.assertEqual(l.lines[0][1], "X")
        self.assertEqual(l.width, 4)
        self.assertEqual(l.height, 2)
        l.set_char(5, 5, "X")
        self.assertEqual(l.lines[5][5], "X")
        self.assertEqual(l.width, 6)
        self.assertEqual(l.height, 6)

    def test_empty_trailing_line(self):
        l = Layer("foo\nBar!\n\n")
        self.assertEqual(l.text, "foo\nBar!\n\n")
        self.assertEqual(l.height, 3)
        self.assertEqual(l.lines, ["foo", "Bar!", ""])

    def test_no_trailing_newline(self):
        l = Layer("foo\nBar!")
        self.assertEqual(l.text, "foo\nBar!\n")
        self.assertEqual(l.color, None)
        self.assertEqual(l.width, 4)
        self.assertEqual(l.height, 2)
        self.assertEqual(l.lines, ["foo", "Bar!"])

    def test_color(self):
        l = Layer("foo\nBar!\n", color.RgbColor(1, 2, 3))
        self.assertEqual(l.text, "foo\nBar!\n")
        self.assertEqual(l.color, color.RgbColor(1, 2, 3))
        self.assertEqual(l.width, 4)
        self.assertEqual(l.height, 2)


class TestFreeColorLayer(test_common.TestCase):
    def test_empty(self):
        l = FreeColorLayer()
        self.assertFalse(l.matrix)
        self.assertEqual(l.width, 0)
        self.assertEqual(l.height, 0)

    def test_set_char(self):
        l = FreeColorLayer()
        self.assertFalse((4, 5) in l.matrix)
        l.set_char(4, 5, "x", color.RgbColor(1, 2, 3))
        self.assertTrue((4, 5) in l.matrix)
        self.assertEqual(l.matrix[(4, 5)], ("x", color.RgbColor(1, 2, 3)))
        self.assertEqual(l.width, 5)
        self.assertEqual(l.height, 6)

        l.set_char(4, 5, "y", color.RgbColor(3, 2, 1))
        self.assertEqual(l.matrix[(4, 5)], ("y", color.RgbColor(3, 2, 1)))
        self.assertEqual(l.width, 5)
        self.assertEqual(l.height, 6)

        l.set_char(1, 1, "y")
        self.assertEqual(l.matrix[(1, 1)], ("y", None))
        self.assertEqual(l.width, 5)
        self.assertEqual(l.height, 6)

    def test_add_layer(self):
        l = FreeColorLayer()
        color_foo = color.RgbColor(0xf, 0, 0)
        l.add_layer(Layer("Foo", color_foo))
        self.assertEqual(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEqual(l.matrix[(1, 0)], ("o", color_foo))
        self.assertEqual(l.matrix[(2, 0)], ("o", color_foo))

        color_ubar = color.RgbColor(0xb, 0xa, 0x2)
        l.add_layer(Layer(" u\n b\n a\n r", color_ubar))
        self.assertEqual(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEqual(l.matrix[(1, 0)], ("u", color_ubar))
        self.assertEqual(l.matrix[(2, 0)], ("o", color_foo))
        self.assertEqual(l.matrix[(1, 1)], ("b", color_ubar))

        color_fun = color.RgbColor(0xf, 0xa, 0xf)
        l.add_layer(Layer("  n\n", color_fun))
        self.assertEqual(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEqual(l.matrix[(1, 0)], ("u", color_ubar))
        self.assertEqual(l.matrix[(2, 0)], ("n", color_fun))

        other = FreeColorLayer()
        other.set_char(3, 0, "!", color_foo)
        l.add_layer(other)
        self.assertEqual(l.matrix[(0, 0)], ("F", color_foo))
        self.assertEqual(l.matrix[(1, 0)], ("u", color_ubar))
        self.assertEqual(l.matrix[(2, 0)], ("n", color_fun))
        self.assertEqual(l.matrix[(3, 0)], ("!", color_foo))

        self.assertRaises(TypeError, lambda: l.add_layer(None))


class TestDocument(test_common.TestCase):
    def test_ctor(self):
        doc = Document()
        self.assertEqual(doc.name, "")
        self.assertEqual(doc.layers, [])
        self.assertEqual(doc.metadata, {})

        doc = Document("foo")
        self.assertEqual(doc.name, "foo")
        self.assertEqual(doc.layers, [])
        self.assertEqual(doc.metadata, {})

        doc = Document("foo", [Layer()], {"foo": "bar"})
        self.assertEqual(doc.name, "foo")
        self.assertEqual(len(doc.layers), 1)
        self.assertEqual(doc.metadata, {"foo": "bar"})

    def test_flatten(self):
        doc = Document()
        layer = doc.flattened()
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.text, "")

        doc.layers.append(Layer("Foo\n", color.RgbColor(1, 2, 3)))
        layer = doc.flattened()
        self.assertIsInstance(layer, Layer)
        self.assertEqual(layer.text, "Foo\n")
        self.assertEqual(layer.color, doc.layers[0].color)

        doc.layers.append(Layer("\nbar\n", color.RgbColor(3, 2, 1)))
        layer = doc.flattened()
        self.assertIsInstance(layer, FreeColorLayer)
        self.assertEqual(layer.matrix[(0, 0)], ("F", color.RgbColor(1, 2, 3)))
        self.assertEqual(layer.matrix[(0, 1)], ("b", color.RgbColor(3, 2, 1)))

        doc2 = doc.flattened_doc()
        self.assertEqual(len(doc2.layers), 1)
        self.assertIsInstance(doc2.layers[0], FreeColorLayer)
        self.assertEqual(doc2.layers[0].matrix, layer.matrix)

    def test_properties(self):
        doc = Document(layers=[Layer("Foo\n\nBar"), Layer("Hello")])
        self.assertEqual(doc.width, 5)
        self.assertEqual(doc.height, 3)


class TestMisc(test_common.TestCase):
    def test_basename(self):
        self.assertEqual(_misc.basename(""), "")
        self.assertEqual(_misc.basename("foo"), "foo")
        self.assertEqual(_misc.basename("foo.bar"), "foo")
        self.assertEqual(_misc.basename("foo.b.a.r"), "foo")
        self.assertEqual(_misc.basename("hello/foo.bar"), "foo")
        self.assertEqual(_misc.basename("hello/foo"), "foo")
        self.assertEqual(_misc.basename("hello.world/foo"), "foo")
        self.assertEqual(_misc.basename("hello.world/foo.bar"), "foo")

    def test_extension(self):
        self.assertEqual(_misc.extension("foo"), "")
        self.assertEqual(_misc.extension("foo.bar"), "bar")
        self.assertEqual(_misc.extension("hello/foo.bar"), "bar")
        self.assertEqual(_misc.extension("hello/foo.b.a.r"), "b.a.r")
        self.assertEqual(_misc.extension("hello.world/foo.bar"), "bar")


#TODO Test formatters

test_common.main()
