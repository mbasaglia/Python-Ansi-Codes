#!/usr/bin/env python
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


class Point(object):
    """
    Point in a 2D plane
    """

    def __init__(self, *args, **kwargs):
        if len(args) == 2:
            if kwargs.get("reversed", False):
                args = reversed(args)
            self.x, self.y = args
        elif len(args) == 1:
            self.x, self.y = args[0]
        else:
            self.x = kwargs.get("x", 0)
            self.y = kwargs.get("y", 0)

    def __iadd__(self, other):
        self.x += other.x
        self.y += other.y
        return self

    def __add__(self, other):
        return Point(
            self.x + other.x,
            self.y + other.y
        )

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y
        return self

    def __sub__(self, other):
        return Point(
            self.x - other.x,
            self.y - other.y
        )

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)

    def interpolate(self, other, factor=0.5):
        def lerp(a, b, factor):
            return int(round(a * (1-factor) + b * factor))
        return Point(
            lerp(self.x, other.x, factor),
            lerp(self.y, other.y, factor)
        )

    def __repr__(self):
        return "(%s, %s)" % (self.x, self.y)

    def __len__(self):
        return 2

    def __getitem__(self, key):
        if key == 0 or key == "x":
            return self.x
        if key == 1 or key == "y":
            return self.y
        raise KeyError(key)

    def __iter__(self):
        yield self.x
        yield self.y


class Rect(object):
    def __init__(self, **kwargs):
        if "pos" in kwargs and "size" in kwargs:
            self._top_left = kwargs["pos"]
            self._bottom_right = self._top_left + kwargs["size"]
        elif "top_left" in kwargs and "bottom_right" in kwargs:
            self._top_left = kwargs["top_left"]
            self._bottom_right = kwargs["bottom_right"]
        elif ( "x" in kwargs and "y" in kwargs and
                "width" in kwargs and "height" in kwargs ):
            self._top_left = Point(kwargs["x"], kwargs["y"])
            self._bottom_right = self._top_left + \
                Point(kwargs["width"], kwargs["height"])
        elif ( "x1" in kwargs and "y1" in kwargs and
                "x2" in kwargs and "y2" in kwargs ):
            self._top_left = Point(kwargs["x1"], kwargs["y1"])
            self._bottom_right = Point(kwargs["x2"], kwargs["y2"])
        elif ( "top" in kwargs and "left" in kwargs and
                "bottom" in kwargs and "right" in kwargs ):
            self._top_left = Point(kwargs["top"], kwargs["left"])
            self._bottom_right = Point(kwargs["bottom"], kwargs["right"])
        else:
            self._top_left = Point()
            self._bottom_right = Point()

    def contains(self, point, inclusive=True):
        if inclusive:
            return self._top_left.x <= point.x <= self._bottom_right.x and \
                   self._top_left.y <= point.y <= self._bottom_right.y
        return self._top_left.x < point.x < self._bottom_right.x and \
               self._top_left.y < point.y < self._bottom_right.y

    @property
    def top(self):
        return self._top_left.y

    @property
    def left(self):
        return self._top_left.x

    @property
    def bottom(self):
        return self._bottom_right.y

    @property
    def right(self):
        return self._bottom_right.x

    @property
    def top_left(self):
        return Point(self.left, self.top)

    @property
    def top_right(self):
        return Point(self.right, self.top)

    @property
    def bottom_left(self):
        return Point(self.left, self.bottom)

    @property
    def bottom_right(self):
        return Point(self.right, self.bottom)

    @property
    def center(self):
        return self._top_left.interpolate(self._bottom_right)

    @property
    def x1(self):
        return self._top_left.x

    @property
    def y1(self):
        return self._top_left.y

    @property
    def x2(self):
        return self._bottom_right.x

    @property
    def y2(self):
        return self._bottom_right.y

    @property
    def x(self):
        return self._top_left.x

    @property
    def y(self):
        return self._top_left.y

    @property
    def width(self):
        return self._bottom_right.x - self._top_left.x

    @property
    def height(self):
        return self._bottom_right.y - self._top_left.y

    @property
    def pos(self):
        return Point(
            self._top_left.x,
            self._top_left.y
        )

    @property
    def size(self):
        return self._bottom_right - self._top_left

    @top_left.setter
    def top_left(self, point):
        self._top_left.x = point.x
        self._top_left.y = point.y

    @bottom_right.setter
    def bottom_right(self, point):
        self._bottom_right.x = point.x
        self._bottom_right.y = point.y

    @top_right.setter
    def top_right(self, point):
        self._bottom_right.x = point.x
        self._top_left.y = point.y

    @bottom_left.setter
    def bottom_left(self, point):
        self._top_left.x = point.x
        self._bottom_right.y = point.y

    @left.setter
    def left(self, val):
        self._top_left.x = val

    @top.setter
    def top(self, val):
        self._top_left.y = val

    @bottom.setter
    def bottom(self, val):
        self._bottom_right.y = val

    @right.setter
    def right(self, val):
        self._bottom_right.x = val

    @x.setter
    def x(self, val):
        width = self.width
        self._top_left.x = val
        self._bottom_right.x = val + width

    @y.setter
    def y(self, val):
        height = self.height
        self._top_left.y = val
        self._bottom_right.y = val + height

    @width.setter
    def width(self, val):
        self._bottom_right.x = self._top_left.x + val

    @height.setter
    def height(self, val):
        self._bottom_right.y = self._top_left.y + val

    @pos.setter
    def pos(self, point):
        size = self.size
        self._top_left.x = point.x
        self._top_left.y = point.y
        self._bottom_right = point + size

    @size.setter
    def size(self, point):
        self.width = point.x
        self.height = point.y

    @center.setter
    def center(self, point):
        size = self.size
        self._top_left.x = point.x - size.x / 2
        self._top_left.y = point.y - size.y / 2
        self._bottom_right = self._top_left + size

    @x1.setter
    def x1(self, val):
        self._top_left.x = val

    @y1.setter
    def y1(self, val):
        self._top_left.y = val

    @x2.setter
    def x2(self, val):
        self._bottom_right.x = val

    @y2.setter
    def y2(self, val):
        self._bottom_right.y = val

    def __eq__(self, other):
        return self._top_left == other._top_left and self._bottom_right == other._bottom_right

    def __ne__(self, other):
        return not (self == other)

    def copy(self):
        return Rect(x1=self.x1, y1=self.y1, x2=self.x2, y2=self.y2)
