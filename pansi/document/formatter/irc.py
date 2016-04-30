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


# TODO Color conversions
class IrcFormatter(object):
    flat = True
    colors = [
        "01", "05", "03", "07", "02", "06", "10", "15",
        "14", "04", "09", "08", "12", "13", "11", "00"
    ]

    def document(self, doc, output):
        self.layer(doc.flattened(), output)

    def layer(self, layer, output):
        if isinstance(layer, tree.Layer):
            output.write(self.color(layer.color) + layer.text)
        elif isinstance(layer, tree.FreeColorLayer):
            prev_color = None
            for y in xrange(layer.height):
                output.write("\x0301,01")
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
            return "\x0f"
        elif isinstance(color, tree.IndexedColor):
            if len(color.palette) == 8:
                bright = 8 if getattr(color.palette, "bright", False) else 0
                code = self.colors[color.index + bright]
            elif len(color.palette) == 16:
                code = self.colors[color.index]
        else:
            raise TypeError("Expected document color")

        return "\x03%s,01" % code


factory.register(IrcFormatter(), "irc")
