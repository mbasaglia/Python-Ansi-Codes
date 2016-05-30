#!/bin/bash
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

SELFDIR=$(dirname $(readlink -se "${BASH_SOURCE[0]}"))
ENV_NAME=.env
ACTIVATE_NAME=activate
FORCE_PYTHON3=false
VIRTUALENV_FLAGS=()

if echo "$1" | grep -qEi "^(python)?3"
then
    FORCE_PYTHON3=true
fi

if $FORCE_PYTHON3
then
    VIRTUALENV_FLAGS+=(-p python3)
    ENV_NAME=.env3
    ACTIVATE_NAME=activate3
fi

if ! which pip virtualenv python &>/dev/null
then
    echo "The following tools are required to set up a virtual environment:"
    echo "    * python"
    echo "    * pip"
    echo "    * virtualenv"
    exit 1
fi

cd "$SELFDIR"
virtualenv "${VIRTUALENV_FLAGS[@]}" "$ENV_NAME"
ln -s "$ENV_NAME/bin/activate" $ACTIVATE_NAME
source $ACTIVATE_NAME
pip install -r requirements.pip
