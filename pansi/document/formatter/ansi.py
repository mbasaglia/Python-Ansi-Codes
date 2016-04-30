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
from ...ansi import SGR


# TODO Standard mode
class AnsiFormatter(object):
    flat = True

    def document(self, doc, output):
        self.layer(doc.flattened(), output)

    def layer(self, layer, output):
        if isinstance(layer, tree.Layer):
            output.write(self.color(layer.color) + layer.text)
        elif isinstance(layer, tree.FreeColorLayer):
            prev_color = None
            for y in xrange(layer.height):
                for x in xrange(layer.width):
                    char, color = layer.matrix.get((x, y), (" ", tree.UnchangedColor))
                    if color is not tree.UnchangedColor and color != prev_color:
                        prev_color = color
                        output.write(self.color(color))
                    output.write(char)
                output.write("\n")
        else:
            raise TypeError("Expected layer type")

    def color(self, color):
        if color is None:
            ansi_color = SGR.ResetColor
        elif isinstance(color, tree.RgbColor):
            ansi_color = SGR.ColorRGB(color.r, color.g, color.b)
        elif isinstance(color, tree.IndexedColor):
            if len(color.palette) == 8:
                bright = getattr(color.palette, "bright", False)
                ansi_color = SGR.Color(color.index, False, bright)
            elif len(color.palette) == 16:
                ansi_color = SGR.Color(color.index & 7, False, color.index > 7)
            else:
                ansi_color = SGR.Color256(color.index)
        elif type(color) is tuple and len(color) == 3:
            ansi_color = SGR.ColorRGB(*color)
        else:
            raise TypeError("Expected document color")

        return repr(SGR(ansi_color))


factory.register(AnsiFormatter(), "ansi")
