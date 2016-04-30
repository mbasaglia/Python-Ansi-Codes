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
from .. import tree
from .. import _misc


_formatters = {}


def register(formatter, file_extension):
    _formatters[file_extension] = formatter


def formatter(file_extension):
    return _formatters[file_extension]


def formatter_for_file(file_name):
    return formatter(_misc.extension(file_name))


def save(document, file, hint=None):
    if type(file) is str:
        with open(file, "w") as file_obj:
            save(document, file_obj, hint)
            return

    if hint is not None:
        fmt = formatter(hint)
    else:
        fmt = formatter_for_file(file.name)

    if isinstance(document, tree.Document):
        fmt.document(document, file)
    else:
        fmt.layer(document, file)


def formats():
    return sorted(_formatters.keys())
