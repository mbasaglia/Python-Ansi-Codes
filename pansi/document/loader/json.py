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
import re

from .. import tree


class JsonLoader(object):
    def _load_json_color(self, color):
        if not color:
            return None
        if re.match("^#[0-9a-fA-F]{6}$", color):
            return tree.RgbColor(color[1:3], color[3:5], color[5:7])
        if color in tree.colors16.names:
            return tree.IndexedColor(str(color), tree.colors16)
        if color in tree.colors256.names:
            return tree.IndexedColor(str(color), tree.colors256)
        return None

    def _load_json_layer(self, json_dict):
        if "chars" in json_dict:
            layer = tree.FreeColorLayer()
            for char in json_dict["chars"]:
                layer.set_char(
                    int(char["x"]),
                    int(char["y"]),
                    char["char"],
                    self._load_json_color(char.get("color", ""))
                )
            return layer

        return tree.Layer(
            json_dict["text"],
            self._load_json_color(json_dict.get("color", ""))
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
