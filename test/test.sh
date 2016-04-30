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

COVERAGE_RUN_FLAGS=(
    run
    --source=patsi
    --branch
    --append
)

COVERAGE_REPORT_FLAGS=(
    report
    -m
)

if [ -t 1 ]
then
    COLORS=true
else
    COLORS=false
fi

function pccolor()
{
    local percent=${1%\%}
    local color

    if [ -z "$percent" ]
    then
        return
    elif [ "$percent" -eq 100 ]
    then
        color="34"
    elif [ "$percent" -gt 70 ]
    then
        color="32"
    elif [ "$percent" -gt 40 ]
    then
        color="33"
    else
        color="31"
    fi
    echo -e "\x1b[1;${color}m"
}

function colorize()
{
    if ! $COLORS
    then
        cat
        return
    fi

    local line
    while read line
    do
        local percent="$(echo "$line" | grep -Eo "[0-9]+%")"
        echo -e "$(pccolor "$percent")$line\x1b[0m"
    done
}

cd "$SELFDIR/.."
if [ \! -f activate ]
then
    ./setup-env.py
fi
source activate


actions=()
while [ "$1" ]
do
    case "$1" in
        run|test|coverage)
            actions+=("$1")
            ;;
        --color|--colour)
            COLORS=true
            ;;
        --no-color|--no-colour)
            COLORS=false
            ;;
    esac
    shift
done

[ "${#actions[@]}" -eq 0 ] && actions=(run coverage)

for action in "${actions[@]}"
do
    case "$action" in
        run|test)
            rm -f .coverage
            find test -type f -name '*.py' -exec coverage "${COVERAGE_RUN_FLAGS[@]}" {} \;
            ;;
        coverage)
            coverage "${COVERAGE_REPORT_FLAGS[@]}" | colorize
            ;;
    esac
done
