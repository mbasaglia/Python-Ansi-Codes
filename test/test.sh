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
extra_args=()
files=()
while [ "$1" ]
do
    case "$1" in
        run|test|coverage|debug)
            actions+=("$1")
            ;;
        --color|--colour)
            COLORS=true
            ;;
        --no-color|--no-colour)
            COLORS=false
            ;;
        test-*.py)
            files=("$TESTS/$1")
            ;;
        *)
            extra_args+=("$1")
            ;;
    esac
    shift
done

# Expand files
if [ "${#files[@]}" -eq 0 ]
then
    while IFS= read -r -d $'\0' file
    do
        files+=("$file")
    done < <(find "${FIND_FLAGS[@]}" -print0)
fi

[ "${#actions[@]}" -eq 0 ] && actions=(run coverage)

for action in "${actions[@]}"
do
    case "$action" in
        debug)
            for file in "${files[@]}"
            do
                rm -f "${file}c"
                PYTHONPATH="$SOURCES" python "$file" "${extra_args[@]}"
            done
            ;;
        run|test)
            cd "$SOURCES"
            rm -f .coverage
            for file in "${files[@]}"
            do
                coverage "${COVERAGE_RUN_FLAGS[@]}" "$file" "${extra_args[@]}" || \
                    fail "Some tests failed"
            done
            ;;
        coverage)
            cd "$SOURCES"
            coverage "${COVERAGE_REPORT_FLAGS[@]}" | colorize
            ;;
    esac
done
