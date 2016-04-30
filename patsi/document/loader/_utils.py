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
import re
from .. import tree


_rgb_color_regex = re.compile("^#[0-9a-fA-F]{6}$")


def string_to_color(color):
    if not color:
        return None
    if _rgb_color_regex.match(color):
        return tree.RgbColor(color[1:3], color[3:5], color[5:7])
    if color in tree.colors16.names:
        return tree.IndexedColor(str(color), tree.colors16)
    if color in tree.colors256.names:
        return tree.IndexedColor(str(color), tree.colors256)
    return None
