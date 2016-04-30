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
from .. import _misc


_loaders = {}


def register(loader, file_extension):
    _loaders[file_extension] = loader


def loader(file_extension):
    return _loaders[file_extension]


def loader_for_file(file_name):
    return loader(_misc.extension(file_name))


# TODO Use libmagic?
def load(file, hint=None):
    if type(file) is str:
        with open(file, "r") as file_obj:
            return load(file_obj, hint)

    if hint is not None:
        ldr = loader(hint)
    else:
        ldr = loader_for_file(file.name)

    return ldr.load_file(file)


def formats():
    return sorted(_loaders.keys())
