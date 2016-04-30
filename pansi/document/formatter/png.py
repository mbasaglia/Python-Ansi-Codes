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
import cairosvg
from StringIO import StringIO

from .. import tree
from .svg import SvgFormatter
from . import factory


class PngFormatter(object):
    flat = True

    def __init__(self, *args, **kwargs):
        self._svg_formatter = SvgFormatter(*args, **kwargs)

    def document(self, doc, output):
        buffer = StringIO()
        self._svg_formatter.document(doc, buffer)
        cairosvg.svg2png(bytestring=buffer.getvalue(), write_to=output)

    def layer(self, layer, output):
        doc = tree.Document
        doc.layers.append(layer)
        self.document(doc, output)

    def color(self, color):
        return ""


factory.register(PngFormatter(), "png")
