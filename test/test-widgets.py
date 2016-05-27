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
import test_common

from patsi.widgets import geometry as geo


class TestPoint(test_common.TestCase):
    def assert_point(self, point, x, y):
        self.assertEquals(point.x, x)
        self.assertEquals(point.y, y)

    def test_ctor(self):
        self.assert_point(geo.Point(), 0, 0)
        self.assert_point(geo.Point(1, 2), 1, 2)
        self.assert_point(geo.Point(1, 2, reversed=True), 2, 1)
        self.assert_point(geo.Point((1, 2)), 1, 2)
        self.assert_point(geo.Point(x=1, y=2), 1, 2)

    def test_add(self):
        self.assert_point(geo.Point(1, 2) + geo.Point(30, 40), 31, 42)

        point = geo.Point(1, 2)
        point += geo.Point(30, 40)
        self.assert_point(point, 31, 42)

        self.assert_point(geo.Point(34, 43) - geo.Point(3, 1), 31, 42)

        point = geo.Point(34, 43)
        point -= geo.Point(3, 1)
        self.assert_point(point, 31, 42)

    def test_cmp(self):
        self.assertTrue(geo.Point(1, 2) == geo.Point(1, 2))
        self.assertFalse(geo.Point(1, 2) == geo.Point(1, 3))
        self.assertFalse(geo.Point(3, 2) == geo.Point(1, 2))

        self.assertFalse(geo.Point(1, 2) != geo.Point(1, 2))
        self.assertTrue(geo.Point(1, 2) != geo.Point(1, 3))
        self.assertTrue(geo.Point(3, 2) != geo.Point(1, 2))

    def test_interpolate(self):
        self.assert_point(geo.Point(4, 5).interpolate(geo.Point(2, 3)), 3, 4)
        self.assert_point(geo.Point(4, 5).interpolate(geo.Point(2, 3), 0), 4, 5)
        self.assert_point(geo.Point(4, 5).interpolate(geo.Point(2, 3), 1), 2, 3)

    def test_elements(self):
        point = geo.Point(4, 5)
        self.assertEquals(point[0], point.x)
        self.assertEquals(point["x"], point.x)
        self.assertEquals(point[1], point.y)
        self.assertEquals(point["y"], point.y)
        self.assertRaises(KeyError, lambda: point[2])
        self.assertRaises(KeyError, lambda: point["z"])

        x, y = point
        self.assert_point(point, x, y)
        self.assertEquals(tuple(point), (x, y))

    def test_repr(self):
        point = geo.Point(4, 5)
        self.assertEquals(str(point), str(tuple(point)))


class TestRect(test_common.TestCase):
    def assert_rect(self, rect, x1, y1, x2, y2):
        self.assertEquals(rect.top_left, geo.Point(x1, y1))
        self.assertEquals(rect.bottom_right, geo.Point(x2, y2))

    def test_ctor(self):
        tl = geo.Point(1, 2)
        br = geo.Point(11, 22)
        sz = geo.Point(10, 20)
        self.assert_rect(geo.Rect(pos=tl, size=sz), 1, 2, 11, 22)
        self.assert_rect(geo.Rect(top_left=tl, bottom_right=br), 1, 2, 11, 22)
        self.assert_rect(
            geo.Rect(x=tl.x, y=tl.y, width=sz.x, height=sz.y),
            1, 2, 11, 22
        )
        self.assert_rect(
            geo.Rect(x1=tl.x, y1=tl.y, x2=br.x, y2=br.y),
            1, 2, 11, 22
        )
        self.assert_rect(
            geo.Rect(top=tl.x, left=tl.y, bottom=br.x, right=br.y),
            1, 2, 11, 22
        )
        self.assert_rect(geo.Rect(), 0, 0, 0, 0)

    def test_contains(self):
        rect = geo.Rect(x1=10, y1=10, x2=20, y2=20)
        pin = geo.Point(12, 13)
        pout = geo.Point(14, 2)
        pbound = geo.Point(14, 10)

        self.assertTrue(rect.contains(pin))
        self.assertFalse(rect.contains(pout))
        self.assertTrue(rect.contains(pbound))

        self.assertTrue(rect.contains(pin, False))
        self.assertFalse(rect.contains(pout, False))
        self.assertFalse(rect.contains(pbound, False))

    def test_property_getters(self):
        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        self.assertEquals(rect.top_left, geo.Point(1, 2))
        self.assertEquals(rect.bottom_right, geo.Point(11, 32))
        self.assertEquals(rect.top_right, geo.Point(11, 2))
        self.assertEquals(rect.bottom_left, geo.Point(1, 32))
        self.assertEquals(rect.center, geo.Point(6, 17))

        self.assertEquals(rect.top, 2)
        self.assertEquals(rect.left, 1)
        self.assertEquals(rect.bottom, 32)
        self.assertEquals(rect.right, 11)

        self.assertEquals(rect.x1, 1)
        self.assertEquals(rect.y1, 2)
        self.assertEquals(rect.x2, 11)
        self.assertEquals(rect.y2, 32)

        self.assertEquals(rect.x, 1)
        self.assertEquals(rect.y, 2)
        self.assertEquals(rect.width, 10)
        self.assertEquals(rect.height, 30)
        self.assertEquals(rect.size, geo.Point(10, 30))

    def test_property_setters(self):
        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.top_left = geo.Point(10, 20)
        self.assert_rect(rect, 10, 20, 11, 32)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.bottom_right = geo.Point(30, 40)
        self.assert_rect(rect, 1, 2, 30, 40)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.top_right = geo.Point(10, 20)
        self.assert_rect(rect, 1, 20, 10, 32)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.bottom_left = geo.Point(40, 20)
        self.assert_rect(rect, 40, 2, 11, 20)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.left = 4
        rect.top = 5
        rect.right = 6
        rect.bottom = 7
        self.assert_rect(rect, 4, 5, 6, 7)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.x = 101
        rect.y = 102
        self.assert_rect(rect, 101, 102, 111, 132)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.width = 100
        rect.height = 200
        self.assert_rect(rect, 1, 2, 101, 202)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.size = geo.Point(100, 200)
        self.assert_rect(rect, 1, 2, 101, 202)

        rect = geo.Rect(x1=1, y1=2, x2=11, y2=32)
        rect.center = geo.Point(0, 0)
        self.assert_rect(rect, -5, -15, 5, 15)


test_common.main()
