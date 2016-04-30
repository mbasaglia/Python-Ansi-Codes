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
from .. import _misc
from ... import ansi


class AnsiLoader(object):
    class _LayerTracker(object):
        def __init__(self, loader, doc_name):
            self.doc = tree.Document(doc_name)
            self.loader = loader
            self.clear()

        def clear(self):
            if self.loader.colors_to_layers:
                self.layers = {}
            else:
                self.doc.layers = [tree.FreeColorLayer()]

        def set_char(self, x, y, ch, color):
            if not self.loader.colors_to_layers:
                self.doc.layers[0].set_char(x, y, ch, color)
                return

            if isinstance(color, tree.IndexedColor):
                index = (len(color.palette), color.index)
            else:
                index = (-1, color.rgb)

            if index not in self.layers:
                layer = tree.Layer("", color)
                self.layers[index] = layer
                self.doc.layers.append(layer)

            self.layers[index].set_char(x, y, ch)

    def __init__(self, colors_to_layers=True):
        self.colors_to_layers = colors_to_layers

    def load_string(self, string, doc_name=""):
        layer_tracker = AnsiLoader._LayerTracker(self, doc_name)

        color = None
        mover = ansi.CharMover(0, 0)
        for item in ansi.AnsiCode.split(string):
            if isinstance(item, ansi.CursorPosition):
                mover.move(item.column - 1, item.row - 1)
            elif isinstance(item, ansi.SGR):
                color = AnsiLoader.color_from_ansi(item)
            elif isinstance(item, ansi.AnsiCode):
                if item == ansi.common.clear_screen:
                    layer_tracker.clear()
            else:
                for ch in mover.loop(item):
                    layer_tracker.set_char(mover.x, mover.y, ch, color)
        return layer_tracker.doc

    def load_file(self, file):
        if type(file) is str:
            with open(file) as f:
                return self.load_file(f)
        else:
            if hasattr(file, "name"):
                name = _misc.basename(file.name)
            else:
                name = ""
            return self.load_string(file.read(), name)

    @staticmethod
    def color_from_ansi(color, background=False):
        if not isinstance(color, ansi.SGR):
            if isinstance(color, ansi.AnsiCode) and color.terminator == 'm':
                color = ansi.SGR(int(arg) for arg in color.args())
            else:
                raise TypeError("Expected SGR ansi code object")

        result = None
        bright = False
        for flag in color.flags:
            if flag == 0:
                result = None
                bright = False
            elif flag == 1:
                bright = True
            elif flag == 22:
                bright = False
            elif isinstance(flag, ansi.SGR.ColorRGB):
                if flag.background == background:
                    result = tree.RgbColor(flag.r, flag.g, flag.b)
            elif isinstance(flag, ansi.SGR.Color):
                if flag.background == background:
                    if flag.color == flag.ResetColor:
                        result = None
                    else:
                        bright = flag.bright or bright
                        result = tree.IndexedColor(flag.color, tree.colors16)
            elif isinstance(flag, ansi.SGR.Color256):
                if flag.background == background:
                    result = tree.IndexedColor(flag.color, tree.colors256)

        if isinstance(result, tree.IndexedColor) and len(result.palette) == 16 and bright:
            result.index += 8

        return result


factory.register(AnsiLoader(), "ansi")
