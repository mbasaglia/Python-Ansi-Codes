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
SOURCES="$SELFDIR/../patsi"
TESTS="$SELFDIR"
VIRTUALENV_PARENT_DIR="$SELFDIR/.."

COVERAGE_RUN_FLAGS=(
    run
    --source="$SOURCES"
    --branch
    --append
)

COVERAGE_REPORT_FLAGS=(
    report
    -m
)

FIND_FLAGS=(
    "$TESTS"
    -type f
    -name '*.py'
    -not -path '*/.env/*'
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
        color="4"
    elif [ "$percent" -gt 70 ]
    then
        color="2"
    elif [ "$percent" -gt 40 ]
    then
        color="3"
    else
        color="1"
    fi
    echo -e "\x1b[9${color}m"
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

function fail()
{
    echo >&2
    echo "$*" >&2
    exit
}

cd "$VIRTUALENV_PARENT_DIR"
if [ \! -f activate ]
then
    ./setup-env.sh
fi

source activate

if ! which coverage &>/dev/null
then
    pip install -r test/requirements-test.pip
fi


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
        debug)
            rm -f *.pyc
            PYTHONPATH="$SOURCES" find "${FIND_FLAGS[@]}" -exec python {} \;
            ;;
        run|test)
            cd "$SOURCES"
            rm -f .coverage
            find "${FIND_FLAGS[@]}" | \
                xargs -n1 coverage "${COVERAGE_RUN_FLAGS[@]}" || \
                fail "Some tests failed"
            ;;
        coverage)
            cd "$SOURCES"
            coverage "${COVERAGE_REPORT_FLAGS[@]}" | colorize
            ;;
    esac
done
