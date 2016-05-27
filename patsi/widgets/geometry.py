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

    def in_window(self, curses_window):
        min = Point(*curses_window.getbegyx(), reversed=True)
        max = Point(*curses_window.getmaxyx(), reversed=True)
        return self.x > min.x and self.x < max.x and self.y > min.y and self.y < max.y

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
