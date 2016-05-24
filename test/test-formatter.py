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
import json
from xml.etree import ElementTree
from mock import patch
import test_common

from patsi import ansi
from patsi.document import tree
from patsi.document import color
from patsi.document import palette
from patsi.document import formatter
from patsi.document.formatter import factory


class TestFactory(test_common.StringOutputTestCase):
    formatters = {
        "ansi": formatter.AnsiFormatter,
        "sh": formatter.AnsiSourceFormatter,
        "py": formatter.AnsiSourceFormatter,
        "pl": formatter.AnsiSourceFormatter,
        "php": formatter.AnsiSourceFormatter,
        "irc": formatter.IrcFormatter,
        "json": formatter.JsonFormatter,
        "png": formatter.PngFormatter,
        "svg": formatter.SvgFormatter,
        "txt": formatter.TextFormatter,
        "xml": formatter.XmlFormatter,
    }

    def test_formatter(self):
        for name, cls in TestFactory.formatters.iteritems():
            self.assertIs(type(factory.formatter(name)), cls)
        self.assertRaises(KeyError, lambda: factory.formatter("____"))

    def test_formats(self):
        self.assertSetEqual(set(TestFactory.formatters), set(factory.formats()))

    def test_formatter_for_file(self):
        for name, cls in TestFactory.formatters.iteritems():
            self.assertIs(type(factory.formatter_for_file("foo." + name)), cls)
        self.assertRaises(KeyError, lambda: factory.formatter_for_file("foo.bar"))

    def test_save(self):
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
        )

        self.output.name = "foo.____"
        self.assertRaises(KeyError, lambda: factory.save(doc, self.output))

        self.output.name = "foo.txt"
        self._clear_data()
        factory.save(doc, self.output, "ansi")
        self._check_data(ansi.SGR(ansi.SGR.Red), "Hello\n",
                         ansi.SGR(ansi.SGR.Blue), "World\n")

        self._clear_data()
        factory.save(doc, self.output)
        self._check_data("Hello\nWorld\n")

        self._clear_data()
        mock_file = test_common.MockFile(self.output)
        with patch("patsi.document.formatter.factory.open", mock_file.open):
            factory.save(doc, "foo/bar.txt")
            self._check_data("Hello\nWorld\n")

        self._clear_data()
        factory.save(doc.layers[0], self.output)
        self._check_data("Hello\n")


class TestAnsiFormatter(test_common.StringOutputTestCase):
    fmt = formatter.AnsiFormatter()

    def test_flat(self):
        self.assertTrue(self.fmt.flat)

    def test_color(self):
        colors = [
            (None, ansi.SGR.ResetColor),
            (color.RgbColor(1, 2, 3), ansi.SGR.ColorRGB(1, 2, 3)),
            (color.IndexedColor(1, palette.colors8_dark), ansi.SGR.Red),
            (color.IndexedColor(1, palette.colors8_bright),
                ansi.SGR.Color(ansi.SGR.Color.Red, bright=True)),
            (color.IndexedColor(1, palette.colors16), ansi.SGR.Red),
            (color.IndexedColor(9, palette.colors16),
                ansi.SGR.Color(ansi.SGR.Color.Red, bright=True)),
            (color.IndexedColor(9, palette.colors256), ansi.SGR.Color256(9)),
        ]

        for doc_col, sgr_col in colors:
            self.assertEquals(self.fmt.color(doc_col), repr(ansi.SGR(sgr_col)))

        self.assertRaises(TypeError, lambda: self.fmt.color(69))

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self.fmt.layer(layer, self.output)
        self._check_data(ansi.SGR(ansi.SGR.Red), layer.text)
        self._clear_data()

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self.fmt.layer(layer, self.output)
        self._check_data(ansi.SGR(ansi.SGR.Red), "Hell", ansi.SGR(ansi.SGR.Blue), "o!\n")
        self._clear_data()

        layer = None
        self.assertRaises(TypeError, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")

    def test_layer_newline_color(self):
        red = color.IndexedColor(1, palette.colors16)
        sgr_red = str(ansi.SGR(ansi.SGR.Red))

        layer = tree.Layer("Hello\nWorld", red)
        self.fmt.layer(layer, self.output)
        self.assertTrue(all(
            line.startswith(sgr_red)
            for line in self._get_data().splitlines()
        ))
        self._clear_data()

        layer = tree.FreeColorLayer()
        self.fmt.layer(layer, self.output)
        layer.set_char(0, 0, "H", red)
        layer.set_char(0, 1, "i", red)
        self.assertTrue(all(
            line.startswith(sgr_red)
            for line in self._get_data().splitlines()
        ))
        self._clear_data()

    def test_document(self):
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
        )
        self.fmt.document(doc, self.output)
        self._check_data(ansi.SGR(ansi.SGR.Red), "Hello\n",
                         ansi.SGR(ansi.SGR.Blue), "World\n")


class TestAnsiSourceFormatter(test_common.StringOutputTestCase):
    fmt = formatter.AnsiSourceFormatter()

    def test_flat(self):
        self.assertTrue(self.fmt.flat)

    def test_color(self):
        self.assertEquals(
            self.fmt.color(color.IndexedColor(1, palette.colors8_dark)),
            r'"\x1b[31m"'+"\n"
        )

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self.fmt.layer(layer, self.output)
        self._check_data(r'"\x1b[31mHello World\n"', "\n")
        self._clear_data()

    def test_document(self):
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
        )
        self.fmt.document(doc, self.output)
        self._check_data(r'"\x1b[31mHello\n\x1b[34mWorld\n"', "\n")


class TestTextFormatter(test_common.StringOutputTestCase):
    fmt = formatter.TextFormatter()

    def test_flat(self):
        self.assertTrue(self.fmt.flat)

    def test_color(self):
        colors = [
            (None, ansi.SGR.ResetColor),
            (color.RgbColor(1, 2, 3), ansi.SGR.ColorRGB(1, 2, 3)),
            (color.IndexedColor(1, palette.colors8_dark), ansi.SGR.Red),
            (color.IndexedColor(1, palette.colors8_bright),
                ansi.SGR.Color(ansi.SGR.Color.Red, bright=True)),
            (color.IndexedColor(1, palette.colors16), ansi.SGR.Red),
            (color.IndexedColor(9, palette.colors16),
                ansi.SGR.Color(ansi.SGR.Color.Red, bright=True)),
            (color.IndexedColor(9, palette.colors256), ansi.SGR.Color256(9)),
        ]

        for doc_col, sgr_col in colors:
            self.assertEquals(self.fmt.color(doc_col), "")

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self.fmt.layer(layer, self.output)
        self._check_data(layer.text)
        self._clear_data()

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self.fmt.layer(layer, self.output)
        self._check_data("Hello!\n")
        self._clear_data()

        layer = None
        self.assertRaises(TypeError, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")

    def test_document(self):
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
        )
        self.fmt.document(doc, self.output)
        self._check_data("Hello\nWorld\n")


class TestIrcFormatter(test_common.StringOutputTestCase):
    fmt = formatter.IrcFormatter()
    irc_colors = formatter.IrcFormatter.colors

    def test_flat(self):
        self.assertTrue(self.fmt.flat)

    def test_color(self):
        self.assertRaises(NotImplementedError, lambda: self.fmt.color(color.RgbColor(1, 2, 255)))
        self.assertRaises(NotImplementedError, lambda: self.fmt.color(color.IndexedColor(9, palette.colors256)))

        colors = [
            #(color.RgbColor(1, 2, 255), self.irc_colors[8+2]),
            (color.IndexedColor(1, palette.colors8_dark), self.irc_colors[1]),
            (color.IndexedColor(1, palette.colors8_bright), self.irc_colors[8+1]),
            (color.IndexedColor(1, palette.colors16), self.irc_colors[1]),
            (color.IndexedColor(9, palette.colors16), self.irc_colors[8+1]),
            #(color.IndexedColor(9, palette.colors256), ???),
        ]

        for doc_col, irc_col in colors:
            self.assertEquals(self.fmt.color(doc_col), "\x03%s,01" % irc_col)

        self.assertEquals(self.fmt.color(None), "\x0f")

        self.assertRaises(TypeError, lambda: self.fmt.color(69))

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self.fmt.layer(layer, self.output)
        self._check_data(self.fmt.color(red), layer.text)

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        self._check_data(self.fmt.color(red), "Hell",
                         self.fmt.color(blue), "o!\n")

        layer = None
        self._clear_data()
        self.assertRaises(TypeError, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")

    def test_layer_newline_color(self):
        red = color.IndexedColor(1, palette.colors16)
        out_red = self.fmt.color(red)

        layer = tree.Layer("Hello\nWorld", red)
        self.fmt.layer(layer, self.output)
        self.assertTrue(all(
            line.startswith(out_red)
            for line in self._get_data().splitlines()
        ))
        self._clear_data()

        layer = tree.FreeColorLayer()
        self.fmt.layer(layer, self.output)
        layer.set_char(0, 0, "H", red)
        layer.set_char(0, 1, "i", red)
        self.assertTrue(all(
            line.startswith(out_red)
            for line in self._get_data().splitlines()
        ))
        self._clear_data()

    def test_document(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)

        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", red),
                tree.Layer("\nWorld", blue),
            ],
        )
        self.fmt.document(doc, self.output)
        self._check_data(self.fmt.color(red), "Hello\n",
                         self.fmt.color(blue), "World\n")


class TestJsonFormatter(test_common.StringOutputTestCase):
    fmt = formatter.JsonFormatter()
    maxDiff = None

    def test_flat(self):
        self.assertFalse(self.fmt.flat)

    def test_color(self):
        colors = [
            (None, ""),
            (color.RgbColor(1, 2, 3), "#010203"),
            (color.IndexedColor(1, palette.colors8_dark), "red"),
            (color.IndexedColor(1, palette.colors8_bright), "red"),
            (color.IndexedColor(1, palette.colors16), "red"),
            (color.IndexedColor(9, palette.colors16), "red_bright"),
            (color.IndexedColor(9, palette.colors256), palette.colors256.name(9)),
        ]

        for doc_col, name in colors:
            self.assertEquals(self.fmt.color(doc_col), '"%s"' % name)

        self.assertRaises(Exception, lambda: self.fmt.color(69))

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self.fmt.layer(layer, self.output)
        self.assertDictEqual(
            json.loads(self._get_data()),
            {"color": red.name, "text": layer.text}
        )
        self._clear_data()

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self.fmt.layer(layer, self.output)
        self.assertDictEqual(
            json.loads(self._get_data()),
            {"chars": [
                {"x": 0, "y": 0, "char": "H", "color": "red"},
                {"x": 1, "y": 0, "char": "e", "color": "red"},
                {"x": 2, "y": 0, "char": "l", "color": "red"},
                {"x": 3, "y": 0, "char": "l", "color": "red"},
                {"x": 4, "y": 0, "char": "o", "color": "blue"},
                {"x": 5, "y": 0, "char": "!", "color": "blue"},
            ]}
        )
        self._clear_data()

        layer = None
        self.assertRaises(TypeError, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")

    def test_document(self):
        metadata = {"hello": "world"}
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
            metadata
        )
        self.fmt.document(doc, self.output)
        self.assertDictEqual(
            json.loads(self._get_data()),
            {
                "layers": [
                    {"color": "red", "text": "Hello\n"},
                    {"color": "blue", "text": "\nWorld\n"},
                ],
                "name": "test",
                "metadata": metadata,
            }
        )


class TestPngFormatter(test_common.StringOutputTestCase):
    fmt = formatter.PngFormatter()

    def test_flat(self):
        self.assertTrue(self.fmt.flat)

    def test_color(self):
        colors = [
            None,
            color.RgbColor(1, 2, 255),
            color.IndexedColor(1, palette.colors8_dark),
            color.IndexedColor(1, palette.colors8_bright),
            color.IndexedColor(1, palette.colors16),
            color.IndexedColor(9, palette.colors16),
            color.IndexedColor(9, palette.colors256),
        ]

        for doc_col in colors:
            self.assertEquals(self.fmt.color(doc_col), "")

    def _check_png_header(self):
        return self._get_data().startswith("PNG")

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self.fmt.layer(layer, self.output)
        self._check_png_header()

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        self._check_png_header()

        layer = None
        self._clear_data()
        self.assertRaises(Exception, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")

    def test_document(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)

        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", red),
                tree.Layer("\nWorld", blue),
            ],
        )
        self.fmt.document(doc, self.output)
        self._check_png_header()


class TestSVGFormatter(test_common.StringOutputTestCase):
    fmt = formatter.SvgFormatter()
    xmlns = "http://www.w3.org/2000/svg"

    def _assert_element(self, elem, name):
        self.assertEquals(elem.tag, "{%s}%s" % (self.xmlns, name))

    def _check_svg(self):
        try:
            elem = ElementTree.fromstring(self._get_data())
            self._assert_element(elem, "svg")
            return elem
        except ElementTree.ParseError as e:
            self.fail("Invalid XML: %s" % e)

    def test_flat(self):
        self.assertFalse(formatter.SvgFormatter().flat)
        self.assertTrue(formatter.SvgFormatter(flatten=True).flat)

    def test_color(self):
        colors = [
            color.RgbColor(1, 2, 255),
            color.IndexedColor(1, palette.colors8_dark),
            color.IndexedColor(1, palette.colors8_bright),
            color.IndexedColor(1, palette.colors16),
            color.IndexedColor(9, palette.colors16),
            color.IndexedColor(9, palette.colors256),
        ]

        for doc_col in colors:
            self.assertEquals(self.fmt.color(doc_col), doc_col.rgb.hex())

        self.assertEquals(self.fmt.color(None), "inherit")

        self.assertRaises(Exception, lambda: self.fmt.color(69))

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        elem = self._check_svg()
        self.assertEquals(len(elem), 2)
        self._assert_element(elem[0], "rect")
        self._assert_element(elem[1], "text")
        self.assertEquals(
            elem.get("width"),
            str(layer.width * self.fmt.font_width)
        )
        self.assertEquals(
            elem.get("height"),
            str(layer.height * self.fmt.font_height)
        )
        self.assertEquals(
            elem[0].get("width"),
            str(layer.width * self.fmt.font_width)
        )
        self.assertEquals(
            elem[0].get("height"),
            str(layer.height * self.fmt.font_height)
        )
        self._assert_element(elem[1][0], "tspan")
        self.assertEquals(elem[1][0].text.strip(), layer.text.strip())

        layer = tree.Layer("Hello&<World>", red)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        elem = self._check_svg()
        self.assertEquals(elem[1][0].text.strip(), layer.text.strip())

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        elem = self._check_svg()
        self.assertEquals(len(elem), 2)
        self._assert_element(elem[0], "rect")
        self._assert_element(elem[1], "text")
        self.assertEquals(
            elem.get("width"),
            str(layer.width * self.fmt.font_width)
        )
        self.assertEquals(
            elem.get("height"),
            str(layer.height * self.fmt.font_height)
        )
        self.assertEquals(
            elem[0].get("width"),
            str(layer.width * self.fmt.font_width)
        )
        self.assertEquals(
            elem[0].get("height"),
            str(layer.height * self.fmt.font_height)
        )
        self.assertEquals(len(elem[1]), len(layer.matrix))
        for x, tspan in enumerate(sorted(elem[1], key=lambda e: float(e.get("x")))):
            self._assert_element(tspan, "tspan")
            self.assertEquals(tspan.text, layer.matrix[(x, 0)][0])
            color_hex = layer.matrix[(x, 0)][1].rgb.hex()
            self.assertIn("fill:%s;" % color_hex, tspan.get("style"))

        layer = None
        self._clear_data()
        self.assertRaises(TypeError, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")

    def test_document_noflat(self):
        metadata = {"hello": "world"}
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
            metadata
        )
        self.fmt.document(doc, self.output)
        elem = self._check_svg()
        self.assertEquals(len(elem), len(doc.layers)+1)
        self._assert_element(elem[0], "rect")

        for i in range(len(doc.layers)):
            self._assert_element(elem[i+1], "text")
            self.assertEquals(
                elem[i+1][0].text.strip(),
                doc.layers[i].text.strip()
            )

    def test_document_flat(self):
        metadata = {"hello": "world"}
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
            metadata
        )
        self.fmt.flat = True
        self.fmt.document(doc, self.output)
        self.fmt.flat = False
        elem = self._check_svg()
        self.assertEquals(len(elem), 2)
        self._assert_element(elem[0], "rect")
        self._assert_element(elem[1], "text")


class TestXMLFormatter(test_common.StringOutputTestCase):
    fmt = formatter.XmlFormatter()

    def _get_xml(self):
        try:
            return ElementTree.fromstring(self._get_data())
        except ElementTree.ParseError as e:
            self.fail("Invalid XML: %s" % e)

    def test_color(self):
        colors = [
            color.RgbColor(1, 2, 255),
            color.IndexedColor(1, palette.colors8_dark),
            color.IndexedColor(1, palette.colors8_bright),
            color.IndexedColor(1, palette.colors16),
            color.IndexedColor(9, palette.colors16),
            color.IndexedColor(9, palette.colors256),
        ]

        for doc_col in colors:
            self.assertEquals(self.fmt.color(doc_col), doc_col.name)

        self.assertEquals(self.fmt.color(None), "")

        self.assertRaises(Exception, lambda: self.fmt.color(69))

    def test_layer(self):
        red = color.IndexedColor(1, palette.colors16)
        blue = color.IndexedColor(4, palette.colors16)
        layer = tree.Layer("Hello World", red)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        elem = self._get_xml()
        self.assertEquals(elem.tag, "layer")
        self.assertEquals(elem.text, layer.text)
        self.assertEquals(elem.get("color"), "red")

        layer = tree.Layer("Hello&<World>", red)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        elem = self._get_xml()
        self.assertEquals(elem.text, layer.text)

        layer = tree.FreeColorLayer()
        layer.set_char(0, 0, "H", red)
        layer.set_char(1, 0, "e", red)
        layer.set_char(2, 0, "l", red)
        layer.set_char(3, 0, "l", red)
        layer.set_char(4, 0, "o", blue)
        layer.set_char(5, 0, "!", blue)
        self._clear_data()
        self.fmt.layer(layer, self.output)
        elem = self._get_xml()
        self.assertEquals(elem.tag, "layer")
        self.assertEquals(len(elem), len(layer.matrix))

        for x, char in enumerate(sorted(elem, key=lambda e: float(e.get("x")))):
            self.assertEquals(char.tag, "char")
            self.assertEquals(char.text, layer.matrix[(x, 0)][0])
            self.assertEquals(char.get("color"), layer.matrix[(x, 0)][1].name)

        layer = None
        self._clear_data()
        self.assertRaises(TypeError, lambda: self.fmt.layer(layer, self.output))
        self._check_data("")


    def test_document(self):
        doc = tree.Document()
        self.fmt.document(doc, self.output)
        elem = self._get_xml()
        self.assertEquals(len(elem), 0)
        self.assertEquals(elem.tag, "document")

        metadata = {"hello": "world"}
        doc = tree.Document(
            "test",
            [
                tree.Layer("Hello", color.IndexedColor(1, palette.colors16)),
                tree.Layer("\nWorld", color.IndexedColor(4, palette.colors16)),
            ],
            metadata
        )
        self._clear_data()
        self.fmt.document(doc, self.output)
        elem = self._get_xml()
        self.assertEquals(len(elem), len(doc.layers)+1)
        self.assertEquals(elem.tag, "document")
        self.assertEquals(elem.get("name"), "test")

        for i, layer in enumerate(elem.findall("layer")):
            self.assertEquals(layer.text, doc.layers[i].text)

        self.assertEquals(elem.find("metadata").find("hello").text, "world")


test_common.main()
