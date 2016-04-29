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
from __future__ import absolute_import
import xml.etree.cElementTree as ElementTree

from . import factory
from ._utils import string_to_color
from .. import tree


class XmlLoader(object):
    def _load_xml_layer(self, element):
        if len(element):
            layer = tree.FreeColorLayer()
            for char in element.findall("char"):
                layer.set_char(
                    int(char.attrib["x"]),
                    int(char.attrib["y"]),
                    char.text,
                    string_to_color(char.get("color", ""))
                )
            return layer

        return tree.Layer(
            element.text,
            string_to_color(element.get("color", ""))
        )

    def load_xml(self, doc_element):
        return tree.Document(
            doc_element.get("name", ""),
            [self._load_xml_layer(layer) for layer in doc_element.findall("layer")],
            doc_element.get("metadata", {}),
        )

    def load_string(self, string):
        return self.load_xml(ElementTree.fromstring(string).getroot())

    def load_file(self, file):
        return self.load_xml(ElementTree.parse(file).getroot())


factory.register(XmlLoader(), "xml")
