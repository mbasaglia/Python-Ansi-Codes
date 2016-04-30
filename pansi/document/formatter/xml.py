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
from .. import tree


class XmlFormatter(object):
    flat = False

    def document_element(self, doc):
        xml_doc = ElementTree.Element("document")
        xml_doc.attrib["name"] = doc.name
        if doc.metadata:
            metadata = ElementTree.SubElement(xml_doc, "metadata")
            for key, val in doc.metadata.iteritems():
                element = ElementTree.SubElement(metadata)
                element.text = val
        for layer in doc.layers:
            xml_doc.append(self.layer_element(layer))
        return xml_doc

    def layer_element(self, layer):
        if isinstance(layer, tree.Layer):
            xml_layer = ElementTree.Element("layer")
            xml_layer.attrib["color"] = self.color(layer.color)
            xml_layer.text = layer.text
            return xml_layer
        elif isinstance(layer, tree.FreeColorLayer):
            xml_layer = ElementTree.Element("layer")
            for pos in sorted(layer.matrix.keys(), key=lambda a: (a[1], a[0])):
                char_xml = ElementTree.SubElement(xml_layer, "char")
                char_xml.attrib["color"] = self.color(layer.matrix[pos][1])
                char_xml.attrib["x"] = str(pos[0])
                char_xml.attrib["y"] = str(pos[1])
                char_xml.text = layer.matrix[pos][0]
            return xml_layer
        else:
            raise TypeError("Expected layer type")

    def write_element(self, element, output):
        ElementTree.ElementTree(element).write(output, "utf-8", True)

    def document(self, doc, output):
        self.write_element(self.document_element(doc), output)

    def layer(self, layer, output):
        self.write_element(self.layer_element(layer), output)

    def color(self, color):
        if color is None:
            return ""
        return color.name


factory.register(XmlFormatter(), "xml")
