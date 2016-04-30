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


class Palette(object):
    def __init__(self, *args):
        if len(args) == 1:
            colors = list(args[0])
        else:
            colors = args

        self.names = [color[0] for color in colors]
        self.colors = [color[1] for color in colors]

    def rgb(self, index):
        return self.colors[index]

    def name(self, index):
        return self.names[index]

    def find_index(self, value):
        if type(value) is tuple:
            return self.colors.index(value)
        return self.names.index(value)

    def __iter__(self):
        for item in zip(self.names, self.colors):
            yield item

    def __iadd__(self, other):
        for name, color in other:
            if name in self.names:
                self.colors[self.names.index(name)] = color
            else:
                self.names.append(name)
                self.colors.append(color)
        return self

    def __len__(self):
        return len(self.colors)

    def __add__(self, other):
        temp = copy.deepcopy(self)
        temp += other
        return temp


colors8_dark = Palette(
    ("black",    (0, 0, 0)),
    ("red",      (178, 24, 24)),
    ("green",    (24, 178, 24)),
    ("yellow",   (178, 104, 24)),
    ("blue",     (59, 59, 255)),
    ("magenta",  (178, 24, 178)),
    ("cyan",     (24, 178, 178)),
    ("white",    (178, 178, 178))
)

colors8_bright = Palette(
    ("black",    (104, 104, 104)),
    ("red",      (255, 84, 84)),
    ("green",    (84, 255, 84)),
    ("yellow",   (214, 214, 70)),
    ("blue",     (84, 84, 255)),
    ("magenta",  (255, 84, 255)),
    ("cyan",     (84, 255, 255)),
    ("white",    (255, 255, 255))
)
colors8_bright.brigth = True

colors16 = colors8_dark + Palette(
    ("%s_bright" % name, value)
    for name, value in colors8_bright
)

colors256 = {} # TODO


class IndexedColor(object):
    def __init__(self, color, palette):
        if type(color) is str:
            self.index = palette.find_index(color)
        else:
            self.index = color

        self.palette = palette

    @property
    def rgb(self):
        return self.palette.rgb(self.index)

    @property
    def name(self):
        return self.palette.name(self.index)

    def __eq__(self, oth):
        return oth is not None and self.rgb == oth.rgb

    def __ne__(self, oth):
        return not (self == oth)


def hex_rgb(rgb):
    return '#%02x%02x%02x' % rgb


class RgbColor(object):
    def __init__(self, r, g, b, name=None):
        self.r = r
        self.g = g
        self.b = b
        self._name = name

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def name(self):
        return self._name if self._name is not None else hex_rgb(self.rgb)

    def __eq__(self, oth):
        return oth is not None and self.rgb == oth.rgb

    def __ne__(self, oth):
        return not (self == oth)


class UnchangedColorType(object):
    pass
UnchangedColor = UnchangedColorType()


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
