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
import formatter
from mock import patch
import six
import test_common

from patsi import ansi
from patsi.document import tree
from patsi.document import loader
from patsi.document import color
from patsi.document import palette
from patsi.document.loader import factory
from patsi.document.loader import _utils


class TestUtils(test_common.TestCase):
    def test_string_to_color(self):
        self.assertEqual(
            _utils.string_to_color("#f0Ba12"),
            color.RgbColor(0xf0, 0xba, 0x12)
        )
        self.assertEqual(
            _utils.string_to_color(""),
            None
        )
        self.assertEqual(
            _utils.string_to_color("blue"),
            palette.colors16.rgb(4)
        )
        self.assertEqual(
            _utils.string_to_color("blue_bright"),
            palette.colors16.rgb(4|8)
        )
        self.assertEqual(
            _utils.string_to_color("NavyBlue"),
            color.IndexedColor(
                palette.colors256.find_index("NavyBlue"),
                palette.colors256,
            )
        )
        self.assertEqual(
            _utils.string_to_color("not_really_a_valid_color"),
            None
        )


class TestFactory(test_common.TestCase):
    loaders = {
        "ansi": loader.AnsiLoader,
        "json": loader.JsonLoader,
        "xml": loader.XmlLoader,
    }

    def test_loader(self):
        for name, cls in six.iteritems(self.loaders):
            self.assertIs(type(factory.loader(name)), cls)
        self.assertRaises(KeyError, lambda: factory.loader("____"))

    def test_loader_for_file(self):
        for name, cls in six.iteritems(self.loaders):
            self.assertIs(type(factory.loader_for_file("foo." + name)), cls)
        self.assertRaises(KeyError, lambda: factory.loader("foo"))

    def test_formats(self):
        self.assertEqual(set(self.loaders.keys()), set(factory.formats()))

    def test_load_file_object(self):
        mock_file = test_common.MockFile()

        self.assertIsInstance(factory.load(mock_file, "ansi"), tree.Document)
        self.assertRaises(KeyError, lambda: factory.load(mock_file, "__"))
        self.assertRaises(Exception, lambda: factory.load(mock_file, "json"))

        del mock_file.name
        self.assertRaises(Exception, lambda: factory.load(mock_file))
        mock_file.name = "foo.ansi"
        self.assertIsInstance(factory.load(mock_file), tree.Document)

    def test_load_file_name(self):
        mock_file = test_common.MockFile()
        with patch("patsi.document.loader.factory.open", mock_file.open):
            self.assertIsInstance(factory.load("foo", "ansi"), tree.Document)
            self.assertRaises(KeyError, lambda: factory.load("foo", "__"))

            self.assertRaises(KeyError, lambda: factory.load("foo"))
            self.assertIsInstance(factory.load("foo.ansi"), tree.Document)


class TestAnsiLoader(test_common.TestCase):
    ldr = loader.AnsiLoader()
    def test_color_from_ansi(self):
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(0)))
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(31, 0)))
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(31, 4)),
            color.IndexedColor(1, palette.colors16)
        )
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(39)))
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.AnsiCode("m", [31])),
            color.IndexedColor(1, palette.colors16)
        )
        self.assertRaises(TypeError, lambda: self.ldr.color_from_ansi(1.2))

        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(31)),
            color.IndexedColor(1, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(91)),
            color.IndexedColor(1|8, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(1, 31)),
            color.IndexedColor(1|8, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(1, 31, 22)),
            color.IndexedColor(1, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(38, 2, 1, 2, 3)),
            color.RgbColor(1, 2, 3)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(38, 5, 42)),
            color.IndexedColor(42, palette.colors256)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(1, 38, 5, 42)),
            color.IndexedColor(42, palette.colors256)
        )

        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(41), True),
            color.IndexedColor(1, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(101), True),
            color.IndexedColor(1|8, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(1, 41), True),
            color.IndexedColor(1|8, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(1, 41, 22), True),
            color.IndexedColor(1, palette.colors16)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(48, 2, 1, 2, 3), True),
            color.RgbColor(1, 2, 3)
        )
        self.assertEqual(
            self.ldr.color_from_ansi(ansi.SGR(48, 5, 42), True),
            color.IndexedColor(42, palette.colors256)
        )

        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(41)))
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(101)))
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(1, 41)))
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(1, 41, 22)))
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(48, 2, 1, 2, 3)))
        self.assertIsNone(self.ldr.color_from_ansi(ansi.SGR(48, 5, 42)))

    def test_load_string(self):
        doc = self.ldr.load_string("Hello")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "Hello\n")

        doc = self.ldr.load_string("Hello\x1b[Hfoo")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "foolo\n")

        doc = self.ldr.load_string("Hello\x1b[31m\nfoo")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 2)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertIsInstance(doc.layers[1], tree.Layer)
        self.assertEqual(doc.layers[0].text, "Hello\n")
        self.assertIsNone(doc.layers[0].color)
        self.assertEqual(doc.layers[1].text, "\nfoo\n")
        self.assertEqual(
            doc.layers[1].color,
            color.IndexedColor(1, palette.colors16)
        )

        doc = self.ldr.load_string("Hello\x1b[38;2;1;2;3m\nfoo")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 2)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertIsInstance(doc.layers[1], tree.Layer)
        self.assertEqual(doc.layers[0].text, "Hello\n")
        self.assertIsNone(doc.layers[0].color)
        self.assertEqual(doc.layers[1].text, "\nfoo\n")
        self.assertEqual(doc.layers[1].color, color.RgbColor(1, 2, 3))

        doc = self.ldr.load_string("Hello\x1b[31m\nfoo\x1b[2J")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 0)

        doc = self.ldr.load_string("Hello\x1b[?25lWorld")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "HelloWorld\n")

    def test_load_string_single_layer(self):
        self.ldr.colors_to_layers = False

        doc = self.ldr.load_string("H\x1b[38;2;1;2;3mell\x1b[31mo")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.FreeColorLayer)
        self.assertEqual(
            doc.layers[0].matrix[(0, 0)],
            ("H", None)
        )
        self.assertEqual(
            doc.layers[0].matrix[(1, 0)],
            ("e", color.RgbColor(1, 2, 3))
        )
        self.assertEqual(
            doc.layers[0].matrix[(2, 0)],
            ("l", color.RgbColor(1, 2, 3))
        )
        self.assertEqual(
            doc.layers[0].matrix[(3, 0)],
            ("l", color.RgbColor(1, 2, 3))
        )
        self.assertEqual(
            doc.layers[0].matrix[(4, 0)],
            ("o", color.IndexedColor(1, palette.colors16))
        )

        self.ldr.colors_to_layers = True

    def test_load_file(self):
        doc = self.ldr.load_file(six.StringIO("Hello"))
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "")
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "Hello\n")

        mock_file = test_common.MockFile(six.StringIO("Hello"))
        with patch("patsi.document.loader.ansi.open", mock_file.open):
            doc = self.ldr.load_file("foo/bar.ansi")
            self.assertIsInstance(doc, tree.Document)
            self.assertEqual(doc.name, "bar")
            self.assertEqual(len(doc.layers), 1)
            self.assertIsInstance(doc.layers[0], tree.Layer)
            self.assertEqual(doc.layers[0].text, "Hello\n")


class TestJsonLoader(test_common.TestCase):
    ldr = loader.JsonLoader()

    def test_document(self):
        doc = self.ldr.load_string("{}")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "")
        self.assertEqual(doc.metadata, {})
        self.assertEqual(len(doc.layers), 0)

        doc = self.ldr.load_string('{"name":"foo"}')
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "foo")
        self.assertEqual(doc.metadata, {})
        self.assertEqual(len(doc.layers), 0)

        doc = self.ldr.load_string('{"name":"foo", "metadata":{"foo":"bar"}}')
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "foo")
        self.assertEqual(doc.metadata, {"foo": "bar"})
        self.assertEqual(len(doc.layers), 0)

    def test_layer(self):
        doc = self.ldr.load_string("""{"layers":[
            {"color": "red", "text": "hello"},
            {"text": "world"},
            {"chars":[
                {"x":0, "y":0, "char":"f"},
                {"x":1, "y":0, "char":"o", "color":"blue"},
                {"x":0, "y":2, "char":"o", "color":"#f00f00"}
            ]}
        ]}""")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 3)

        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "hello\n")
        self.assertEqual(
            doc.layers[0].color,
            color.IndexedColor(1, palette.colors16)
        )

        self.assertIsInstance(doc.layers[1], tree.Layer)
        self.assertEqual(doc.layers[1].text, "world\n")
        self.assertIsNone(doc.layers[1].color)

        self.assertIsInstance(doc.layers[2], tree.FreeColorLayer)
        self.assertEqual(doc.layers[2].matrix[(0, 0)][0], "f")
        self.assertIsNone(doc.layers[2].matrix[(0, 0)][1])
        self.assertEqual(doc.layers[2].matrix[(1, 0)][0], "o")
        self.assertEqual(
            doc.layers[2].matrix[(1, 0)][1],
            color.IndexedColor(4, palette.colors16)
        )
        self.assertEqual(doc.layers[2].matrix[(0, 2)][0], "o")
        self.assertEqual(
            doc.layers[2].matrix[(0, 2)][1],
            color.RgbColor(0xf0, 0x0f, 0x00)
        )

    def test_load_file(self):
        doc_string = '{"layers":[{"text":"Hello"}]}'
        doc = self.ldr.load_file(six.StringIO(doc_string))
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "Hello\n")

        mock_file = test_common.MockFile(six.StringIO(doc_string))
        with patch("patsi.document.loader.json.open", mock_file.open):
            doc = self.ldr.load_file("foo/bar.json")
            self.assertIsInstance(doc, tree.Document)
            self.assertEqual(len(doc.layers), 1)
            self.assertIsInstance(doc.layers[0], tree.Layer)
            self.assertEqual(doc.layers[0].text, "Hello\n")


class TestXmlLoader(test_common.TestCase):
    ldr = loader.XmlLoader()

    def test_document(self):
        doc = self.ldr.load_string("<document></document>")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "")
        self.assertEqual(doc.metadata, {})
        self.assertEqual(len(doc.layers), 0)

        doc = self.ldr.load_string("""<document name="foo"></document>""")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "foo")
        self.assertEqual(doc.metadata, {})
        self.assertEqual(len(doc.layers), 0)

        doc = self.ldr.load_string("""<document name="foo">
                <metadata><foo>bar</foo></metadata>
            </document>""")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(doc.name, "foo")
        self.assertEqual(doc.metadata, {"foo": "bar"})
        self.assertEqual(len(doc.layers), 0)

    def test_layer(self):
        doc = self.ldr.load_string("""<document>
            <layer color="red">hello</layer>
            <layer>world</layer>
            <layer>
                <char x="0" y="0">f</char>
                <char x="1" y="0" color="blue">o</char>
                <char x="0" y="2" color="#f00f00">o</char>
            </layer>
        </document>""")
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 3)

        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "hello\n")
        self.assertEqual(
            doc.layers[0].color,
            color.IndexedColor(1, palette.colors16)
        )

        self.assertIsInstance(doc.layers[1], tree.Layer)
        self.assertEqual(doc.layers[1].text, "world\n")
        self.assertIsNone(doc.layers[1].color)

        self.assertIsInstance(doc.layers[2], tree.FreeColorLayer)
        self.assertEqual(doc.layers[2].matrix[(0, 0)][0], "f")
        self.assertIsNone(doc.layers[2].matrix[(0, 0)][1])
        self.assertEqual(doc.layers[2].matrix[(1, 0)][0], "o")
        self.assertEqual(
            doc.layers[2].matrix[(1, 0)][1],
            color.IndexedColor(4, palette.colors16)
        )
        self.assertEqual(doc.layers[2].matrix[(0, 2)][0], "o")
        self.assertEqual(
            doc.layers[2].matrix[(0, 2)][1],
            color.RgbColor(0xf0, 0x0f, 0x00)
        )

    def test_load_file(self):
        doc_string = '<document><layer>Hello</layer></document>'
        doc = self.ldr.load_file(six.StringIO(doc_string))
        self.assertIsInstance(doc, tree.Document)
        self.assertEqual(len(doc.layers), 1)
        self.assertIsInstance(doc.layers[0], tree.Layer)
        self.assertEqual(doc.layers[0].text, "Hello\n")


test_common.main()
