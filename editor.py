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
import os
import sys
import curses
import curses.ascii
from contextlib import contextmanager

from patsi import ansi
from patsi import document


@contextmanager
def curses_context():
    stdscr = curses.initscr()
    curses.noecho()
    curses.cbreak()
    stdscr.keypad(1)
    curses.start_color()
    curses.use_default_colors()

    curses.init_pair(1, curses.COLOR_BLACK,     -1)
    curses.init_pair(2, curses.COLOR_RED,       -1)
    curses.init_pair(3, curses.COLOR_GREEN,     -1)
    curses.init_pair(4, curses.COLOR_YELLOW,    -1)
    curses.init_pair(5, curses.COLOR_BLUE,      -1)
    curses.init_pair(6, curses.COLOR_MAGENTA,   -1)
    curses.init_pair(7, curses.COLOR_CYAN,      -1)
    curses.init_pair(8, curses.COLOR_WHITE,     -1)

    try:
        yield stdscr
    finally:
        stdscr.keypad(0);
        curses.nocbreak();
        curses.echo()
        curses.endwin()


class Point(object):
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

    def __add__(self, other):
        return Point(
            self.x + other.x,
            self.y + other.y
        )

    def __isub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __sub__(self, other):
        return Point(
            self.x - other.x,
            self.y - other.y
        )

    def in_window(self, curses_window):
        min = Point(*curses_window.getbegyx(), reversed=True)
        max = Point(*curses_window.getmaxyx(), reversed=True)
        return x > min.x and x < max.x and y > min.y and y < max.y


class Editor(object):
    def __init__(self, window):
        self.document = document.Document()
        self.active_layer = None
        self.file = ""
        self.cursor = Point()
        self.offset = Point(1, 1)
        self.message = ""
        self.window = window

    def open(self, file):
        self.document = document.loader.factory.load(file)
        self.file = file
        if self.document.layers:
            self.active_layer = self.document.layers[-1]
        else:
            self.active_layer = None

    def render_picture(self):
        layer = self.document.flattened()
        win_height, win_width = self.window.getmaxyx()

        for pos, item in layer.matrix.iteritems():
            pos = Point(pos) + self.offset
            if pos.x < 1 or pos.y < 1 or pos.x >= win_width - 1 or pos.y >= win_height-1:
                continue
            char, col = item
            self.window.addstr(pos.y, pos.x, char, self._color_to_curses(col))


    def render_ui(self):
        win_height, win_width = self.window.getmaxyx()

        self.window.border(
            "|" if self.offset.x >= 1 else ":",
            "|" if self.offset.x + self.document.width < win_width - 1 else ":",
            "_" if self.offset.y >= 1 else ".",
            "_" if self.offset.y + self.document.height < win_height - 1 else ".",
            " ", " ", "|", "|")

        def footer(str, *args, **kwargs):
            self.window.addstr(footer.y, footer.x, str, *args, **kwargs)
            footer.x += len(str) + 1
        footer.x = 1
        footer.y = win_height - 1


        footer("%2s, %2s" % (self.cursor.x, self.cursor.y))
        footer(self._active_color_name(), self._active_color())
        if self.message:
            footer(" -- %s" % self.message)

    def render_cursor(self):
        self.window.move(
            self.cursor.y + self.offset.y,
            self.cursor.x + self.offset.x
        )
        self.window.chgat(1, self._active_color())

    def _color_to_curses(self, color):
        if color is None:
            return curses.A_NORMAL | curses.color_pair(0)
        flags = curses.color_pair((color.index & 7) + 1)
        if color.index & 8:
            flags |= curses.A_BOLD
        return flags

    def _active_color(self):
        if self.active_layer:
            return self._color_to_curses(self.active_layer.color)
        return self._color_to_curses(None)

    def _active_color_name(self):
        if self.active_layer:
            return self.active_layer.color.name
        return ""

    def set_char(self, char):
        if self.active_layer:
            self.active_layer.set_char(self.cursor.x, self.cursor.y, char)

    def text_event(self, ch):
        self.set_char(ch)
        self.cursor.x += 1
        self._adjust_cursor()

    def key_event(self, key):
        if key == curses.KEY_LEFT:
            self.cursor.x -= 1
        elif key == curses.KEY_RIGHT:
            self.cursor.x += 1
        elif key == curses.KEY_UP:
            self.cursor.y -= 1
        elif key == curses.KEY_DOWN or key == curses.KEY_ENTER:
            self.cursor.y += 1
        elif key == curses.KEY_HOME:
            self.cursor.x = 0
        elif key == curses.KEY_END:
            self.cursor.x = self.document.width
        elif key == curses.KEY_SHOME:
            self.cursor.y = 0
        elif key == curses.KEY_SEND:
            self.cursor.y = self.document.height
        elif key == curses.KEY_BACKSPACE:
            self.cursor.x -= 1
            self.set_char(" ") # TODO Remove the char
        elif key == curses.KEY_DC:
            self.set_char(" ") # TODO Remove the char
            self.cursor.x += 1
        self._adjust_cursor()

    def resize_event(self, width, height):
        self._adjust_cursor()

    def _adjust_cursor(self):
        if self.cursor.x < 0:
            self.cursor.x = 0

        if self.cursor.y < 0:
            self.cursor.y = 0

        win_height, win_width = self.window.getmaxyx()

        if self.cursor.y + self.offset.y >= win_height - 1:
            self.offset.y = win_height - 2 - self.cursor.y
        elif self.cursor.y + self.offset.y < 1:
            self.offset.y = 1 - self.cursor.y

        if self.cursor.x + self.offset.x >= win_width - 1:
            self.offset.x = win_width - 2 - self.cursor.x
        elif self.cursor.x + self.offset.x < 1:
            self.offset.x = 1 - self.cursor.x

    @property
    def name(self):
        return self.document.name or os.path.basename(self.file)

    def mouse_event(self, pos, bstate):
        if bstate == curses.BUTTON1_CLICKED:
            self.cursor = pos


class Manager(object):
    def __init__(self, screen):
        self.screen = screen
        self.editors = []
        self.current_editor = None
        self.edit_mode = False

        height, width = screen.getmaxyx()
        self.editor_window = curses.newwin(height-1, width, 1, 0)

    def open_tab(self, file=None):
        editor = Editor(self.editor_window)
        if file is not None:
            try:
                editor.open(file)
            except Exception:
                return
        self.editors.append(editor)
        self.edit_mode = True
        self.current_editor = self.editors[-1]

    def loop(self):
        self._render_title()
        while True:
            if self.edit_mode:
                self._render_document()
            self._get_input()

    def _render_document(self):
        if self.current_editor:
            self.editor_window.clear()
            self.current_editor.render_picture()
            self.current_editor.render_ui()
            if self.edit_mode:
                self.current_editor.render_cursor()
            self.editor_window.refresh()

    def _render_title(self):
        x = 0
        screen.addstr(0, x, "|")
        x += 1
        for editor in self.editors:
            if editor is not self.current_editor:
                mode = curses.A_NORMAL
            elif self.edit_mode:
                mode = curses.A_UNDERLINE
            else:
                mode = curses.A_REVERSE
            screen.addstr(0, x, editor.name, mode)
            x += len(editor.name)
            screen.addstr(0, x, "|")
            x += 1
        screen.refresh()

    def _render(self):
        self.screen.clear()
        self._render_title()
        self._render_document()
        self.screen.refresh()

    def resize_event(self, width, height):
        self.editor_window.resize(screen_height-1, screen_width)
        if self.current_editor:
            self.current_editor.resize_event(screen_height-1, screen_width)

    def mouse_event(self, pos, bstate):
        if pos.in_window(self.editor_window):
            if  self.edit_mode:
                relative = pos - self.current_editor.offset - min
                self.current_editor.mouse_event(relative, bstate)

    def text_event(self, char):
        if self.edit_mode:
            self.current_editor.text_event(char)

    def key_event(self, key):
        if key == 0x1b: # Escape
            if self.edit_mode:
                self.edit_mode = False
                curses.curs_set(0)
            elif self.current_editor:
                self.edit_mode = True
                curses.curs_set(1)
            self._render()
        elif self.edit_mode:
            self.current_editor.key_event(key)
        elif key == curses.KEY_UP:
            self._switch_layer(+1)
        elif key == curses.KEY_DOWN:
            self._switch_layer(-1)
        elif key == curses.KEY_LEFT:
            self._switch_document(-1)
        elif key == curses.KEY_RIGHT:
            self._switch_document(+1)

    def _get_input(self):
        ch = self.screen.getch()
        if ch == curses.KEY_RESIZE:
            screen_height, screen_width = self.screen.getmaxyx()
            self.resize_event(screen_width, screen_height);
        elif ch == curses.KEY_MOUSE:
            try:
                id, x, y, z, bstate = curses.getmouse()
            except curses.error:
                pass
            self.mouse_event(Point(x, y), bstate)
        elif curses.ascii.isprint(ch):
            self.text_event(chr(ch))
        else:
            self.key_event(ch)

    def _switch_layer(self, delta):
        if not self.current_editor or not self.current_editor.document.layers:
            return
        self.current_editor.active_layer = next_object(
            self.current_editor.document.layers,
            self.current_editor.active_layer,
            delta
        )
        self._render_document()

    def _switch_document(self, delta):
        if not self.editors:
            return
        self.current_editor = next_object(self.editors, self.current_editor, delta)
        self._render()


def next_object(array, current, delta):
    index = array.index(current) + delta
    if index >= 0 and index < len(array):
        return array[index]
    return current


with curses_context() as screen:
    curses.mousemask(curses.ALL_MOUSE_EVENTS)
    manager = Manager(screen)
    for file in sys.argv[1:]:
        manager.open_tab(file)
    with ansi.keyboard_interrupt():
        manager.loop()
