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
import six
from xml.sax.saxutils import escape
from contextlib import contextmanager

from . import factory
from .. import tree
from .. import color
from .. import palette


class SvgFormatter(object):

    def __init__(
            self,
            flatten=False,
            background=color.IndexedColor(0, palette.colors8_dark),
            text_color=color.IndexedColor(7, palette.colors8_dark),
            font_size=12):
        self.flat = flatten
        self.background = background
        self.text_color = text_color
        self.font_size = font_size

    @property
    def font_width(self):
        return self.font_size / 2.0

    @property
    def font_height(self):
        return self.font_size

    def document(self, doc, output):
        with self.wrap_svg(doc, output):
            if self.flat:
                self.layer(doc.flattened(), output, True)
            else:
                for layer in doc.layers:
                    self.layer(layer, output, True)

    @contextmanager
    def wrap_svg(self, element, output):
        width = element.width * self.font_width
        height = element.height * self.font_height

        output.write("<?xml version='1.0' encoding='UTF-8' ?>\n")
        output.write("<svg xmlns='http://www.w3.org/2000/svg' width='%s' height='%s'>\n" % (width, height))
        output.write("<rect style='fill:%s;stroke:none;' width='%s' height='%s' x='0' y='0' />\n" % (
            self.color(self.background),
            width,
            height
        ))

        yield

        output.write("</svg>\n")


    def layer(self, layer, output, bare=False):
        if not bare and (
                isinstance(layer, tree.Layer) or
                isinstance(layer, tree.FreeColorLayer)
        ):
            with self.wrap_svg(layer, output):
                return self.layer(layer, output, True)

        css = [
            "font-family:monospace",
            "font-size:%spx" % self.font_size,
            "font-weight:%s" % self.color(self.text_color),
            "fill:white",
        ]

        def open_rect():
            return "<text y='0' x='0' style='%s' xml:space='preserve'>\n" % ";".join(css)

        if isinstance(layer, tree.Layer):
            css.append("fill:%s" % self.color(layer.color))
            css.append("letter-spacing:-%spx" % (self.font_width * 0.2))
            output.write(open_rect())
            y = 0
            for line in layer.lines:
                y += 1
                if line:
                    output.write("<tspan x='{x}' y='{y}'>{line}</tspan>\n".format(
                        x=0,
                        y=y * self.font_height,
                        line=escape(line)
                    ))
        elif isinstance(layer, tree.FreeColorLayer):
            output.write(open_rect())
            prev_color = None
            for pos, item in six.iteritems(layer.matrix):
                char, col = item
                if col is not color.UnchangedColor and col != prev_color:
                    prev_color = col
                output.write("<tspan x='{x}' y='{y}' style='fill:{color};'>{char}</tspan>\n".format(
                    x=pos[0] * self.font_width,
                    y=pos[1] * self.font_height,
                    color=self.color(prev_color),
                    char=escape(char)
                ))
        else:
            raise TypeError("Expected layer type")

        output.write("</text>\n")

    def color(self, color):
        if color is None:
            return "inherit"
        return color.rgb.hex()


factory.register(SvgFormatter(), "svg")
