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
from ._utils import string_to_color


class JsonLoader(object):
    def _load_json_layer(self, json_dict):
        if "chars" in json_dict:
            layer = tree.FreeColorLayer()
            for char in json_dict["chars"]:
                layer.set_char(
                    int(char["x"]),
                    int(char["y"]),
                    char["char"],
                    string_to_color(char.get("color", ""))
                )
            return layer

        return tree.Layer(
            json_dict["text"],
            string_to_color(json_dict.get("color", ""))
        )

    def load_json(self, json_dict):
        return tree.Document(
            json_dict.get("name", ""),
            [self._load_json_layer(layer) for layer in json_dict.get("layers", [])],
            json_dict.get("metadata", {}),
        )

    def load_string(self, string):
        return self.load_json(json.loads(string))

    def load_file(self, file):
        if type(file) is str:
            with open(file) as f:
                return self.load_file(f)
        return self.load_json(json.load(file))


factory.register(JsonLoader(), "json")
