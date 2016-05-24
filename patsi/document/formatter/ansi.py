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
from . import factory
from .. import tree
from .. import color
from ...ansi import SGR


# TODO Standard mode
class AnsiFormatter(object):
    flat = True

    def document(self, doc, output):
        self.layer(doc.flattened(), output)

    def layer(self, layer, output):
        if isinstance(layer, tree.Layer):
            for line in layer.text.splitlines(True):
                output.write(self.color(layer.color) + line)
        elif isinstance(layer, tree.FreeColorLayer):
            for y in xrange(layer.height):
                prev_color = None
                for x in xrange(layer.width):
                    char, col = layer.matrix.get((x, y), (" ", color.UnchangedColor))
                    if col is not color.UnchangedColor and col != prev_color:
                        prev_color = col
                        output.write(self.color(col))
                    output.write(char)
                output.write("\n")
        else:
            raise TypeError("Expected layer type")

    def color(self, c):
        if c is None:
            ansi_color = SGR.ResetColor
        elif isinstance(c, color.RgbColor):
            ansi_color = SGR.ColorRGB(c.r, c.g, c.b)
        elif isinstance(c, color.IndexedColor):
            if len(c.palette) == 8:
                bright = getattr(c.palette, "bright", False)
                ansi_color = SGR.Color(c.index, False, bright)
            elif len(c.palette) == 16:
                ansi_color = SGR.Color(c.index & 7, False, c.index > 7)
            else:
                ansi_color = SGR.Color256(c.index)
        else:
            raise TypeError("Expected document color")

        return repr(SGR(ansi_color))


factory.register(AnsiFormatter(), "ansi")
