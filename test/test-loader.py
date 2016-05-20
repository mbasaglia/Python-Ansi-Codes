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
import test_common

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
        for name, cls in self.loaders.iteritems():
            self.assertIs(type(factory.loader(name)), cls)
        self.assertRaises(KeyError, lambda: factory.loader("____"))

    def test_loader_for_file(self):
        for name, cls in self.loaders.iteritems():
            self.assertIs(type(factory.loader_for_file("foo." + name)), cls)
        self.assertRaises(KeyError, lambda: factory.loader("foo"))

    def test_formats(self):
        self.assertEquals(set(self.loaders.keys()), set(factory.formats()))

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


test_common.main()
