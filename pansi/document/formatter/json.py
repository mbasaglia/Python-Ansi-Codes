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
import json
from . import factory
from .. import tree


class JsonFormatter(object):
    flat = False

    def __init__(self, indent=4, separators=None, sort_keys=False):
        self.indent = indent
        self.separators = separators
        self.sort_keys = sort_keys

    def document_dict(self, doc):
        return {
            "name": doc.name,
            "metadata": doc.metadata,
            "layers": [self.layer_dict(layer) for layer in doc.layers]
        }

    def layer_dict(self, layer):
        if isinstance(layer, tree.Layer):
            return {
                "color": self.color_dict(layer.color),
                "text": layer.text
            }
        elif isinstance(layer, tree.FreeColorLayer):
            return {
                "chars": [
                    {
                        "x": pos[0],
                        "y": pos[1],
                        "char": layer.matrix[pos][0],
                        "color": self.color_dict(layer.matrix[pos][1]),
                    }
                    for pos in
                    sorted(layer.matrix.keys(), key=lambda a: (a[1], a[0]))
                ]
            }
        else:
            raise TypeError("Expected layer type")

    def color_dict(self, color):
        if color is None:
            return ""
        return color.name

    def _json_args(self):
        return {
            "indent": self.indent,
            "separators": self.separators,
            "sort_keys": self.sort_keys,
        }

    def document(self, doc, output):
        json.dump(self.document_dict(doc), output, **self._json_args())

    def layer(self, layer, output):
        json.dump(self.layer_dict(layer), output, **self._json_args())

    def color(self, color):
        json.dumps(self.color_dict(color), **self._json_args())


factory.register(JsonFormatter(), "json")
