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

test_common.main()
