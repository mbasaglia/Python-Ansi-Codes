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
import copy
from ..ansi import CharMover


class Document(object):
    def __init__(self, name="", layers=[], metadata={}):
        self.name = name
        self.layers = layers
        self.metadata = metadata

    def flattened(self):
        if len(self.layers) == 0:
            return Layer()
        if len(self.layers) == 1:
            return copy.deepcopy(self.layers[0])

        flattened = FreeColorLayer(
            max(layer.width for layer in self.layers),
            max(layer.height for layer in self.layers)
        )

        for layer in self.layers:
            flattened.add_layer(layer)

        return flattened

    def flattened_doc(self):
        return Document(self.name, [self.flattened()])

    @property
    def width(self):
        return max(layer.width for layer in self.layers)

    @property
    def height(self):
        return max(layer.height for layer in self.layers)


class Layer(object):
    def __init__(self, text="", color=None):
        if text.endswith("\n"):
            text = text[:-1]
        self.lines = text.split("\n") if text else []
        self.color = color

    @property
    def width(self):
        return max(len(line) for line in self.lines) if self.lines else 0

    @property
    def height(self):
        return len(self.lines)

    @property
    def text(self):
        if not self.lines:
            return ""
        return "\n".join(self.lines) + "\n"

    def set_char(self, x, y, char):
        if y >= self.height:
            self.lines += [""] * (y - self.height + 1)
        if x >= len(self.lines[y]):
            self.lines[y] += " " * (x - len(self.lines[y]) + 1)

        self.lines[y] = self.lines[y][:x] + char + self.lines[y][x + 1:]


class FreeColorLayer(object):
    def __init__(self, width=0, height=0):
        self.matrix = {}
        self.width = width
        self.height = height

    def set_char(self, x, y, char, color=None):
        if y >= self.height:
            self.height = y + 1
        if x >= self.width:
            self.width = x + 1

        self.matrix[(x, y)] = (char, color)

    def add_layer(self, layer, offset_x=0, offset_y=0):
        mover = CharMover(offset_x, offset_y)
        if isinstance(layer, Layer):
            for ch in mover.loop(layer.text):
                self.set_char(mover.x, mover.y, ch, layer.color)
        elif isinstance(layer, FreeColorLayer):
            self.matrix.update(layer.matrix)
        else:
            raise TypeError("Expected Layer")
