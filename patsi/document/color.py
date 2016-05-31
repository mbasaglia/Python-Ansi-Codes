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


class IndexedColor(object):
    """
    Color within a palette
    """
    def __init__(self, color, palette):
        if type(color) is str:
            self.index = palette.find_index(color)
        else:
            self.index = color

        self.palette = palette

    @property
    def rgb_tuple(self):
        """
        Returns a tuple with the rgb components
        """
        return self.palette.rgb_tuple(self.index)

    @property
    def rgb(self):
        """
        Returns a RgbColor object corresponding to this color
        """
        return self.palette.rgb(self.index)

    @property
    def name(self):
        """
        Color name as from the palette
        """
        return self.palette.name(self.index)

    def __eq__(self, oth):
        """
        Compares the rgb tuple of two colors to check whether they are the same
        """
        return self.rgb_tuple == RgbColor._color_tuple(oth)

    def __ne__(self, oth):
        """
        Compares the rgb tuple of two colors to check whether they are the same
        """
        return not (self == oth)

    def __hash__(self):
        return hash((IndexedColor, self.index, self.palette))


class RgbColor(object):
    """
    24 Bit RGB color
    """
    def __init__(self, r, g, b, name=None):
        self.r = r
        self.g = g
        self.b = b
        self._name = name

    @property
    def rgb_tuple(self):
        """
        Returns a tuple with the rgb components
        """
        return (self.r, self.g, self.b)

    @property
    def rgb(self):
        """
        Returns a RgbColor object corresponding to this color
        """
        return self

    @property
    def name(self):
        """
        Color name (if set) otherwise the hex string
        """
        return self._name if self._name is not None else self.hex()

    @name.setter
    def name(self, name):
        """
        Sets the color name to a specific string
        """
        self._name = name

    @name.deleter
    def name(self):
        """
        Resets the name to the default (which is the same as hex)
        """
        self._name = None

    def __eq__(self, oth):
        """
        Compares the rgb tuple of two colors to check whether they are the same
        """
        return self.rgb_tuple == RgbColor._color_tuple(oth)

    def __ne__(self, oth):

        """
        Compares the rgb tuple of two colors to check whether they are the same
        """
        return not (self == oth)

    def copy(self):
        """
        Returns a deep copy of this object
        """
        return RgbColor(self.r, self.g, self.b, self.name)

    def hex(self):
        """
        Hex string for this color
        """
        return '#%02x%02x%02x' % self.rgb_tuple

    @staticmethod
    def _color_tuple(obj):
        """
        Returns a rgb tuple for comaring color-like objects
        """
        if obj is None:
            return tuple()
        if type(obj) is tuple and len(obj) == 3:
            return obj
        return obj.rgb_tuple

    def __hash__(self):
        return hash((RgbColor, self.rgb_tuple))


class UnchangedColorType(object):
    """
    Dummy class for the UnchangedColor constant
    """
    pass
UnchangedColor = UnchangedColorType()


