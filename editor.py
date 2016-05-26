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

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __ne__(self, other):
        return not (self == other)

    def in_window(self, curses_window):
        min = Point(*curses_window.getbegyx(), reversed=True)
        max = Point(*curses_window.getmaxyx(), reversed=True)
        return self.x > min.x and self.x < max.x and self.y > min.y and self.y < max.y

    def __repr__(self):
        return "(%s, %s)" % (self.x, self.y)


class Event(object):
    TYPE_TEXT       = 1
    TYPE_KEY        = 2
    TYPE_RESIZE     = 3
    TYPE_MOUSE      = 4
    TYPE_FOCUS      = 5

    def __init__(self, type, **kwargs):
        self.type = type
        self.propagate = True
        for attr, val in kwargs.iteritems():
            setattr(self, attr, val)

    def accept(self):
        self.propagate = False

    @staticmethod
    def text_event(char):
        return Event(Event.TYPE_TEXT, char=char)

    @staticmethod
    def key_event(key):
        return Event(Event.TYPE_KEY, key=key)

    @staticmethod
    def resize_event(bounds):
        return Event(Event.TYPE_RESIZE, bounds=bounds)

    @staticmethod
    def mouse_event(pos, buttons):
        return Event(Event.TYPE_MOUSE, pos=pos, buttons=buttons)

    @staticmethod
    def focus_event(focus):
        return Event(Event.TYPE_FOCUS, focus=focus)


class Widget(object):
    def __init__(self, parent, window=None):
        self.parent = parent
        self.children = []
        self.focus_child = None
        self.active = True
        self.window = window

        if parent is not None:
            bounds = self.window_bounds_hint(parent.window_bounds())
            if window is None:
                min, max = bounds
                size = max - min
                self.window = parent.window.subwin(size.y, size.x, min.y, min.x)
            else:
                self.adjust_window_size(bounds)
            parent.children.append(self)
        elif window is None:
            self.window = curses.newwin(24, 80)

    def focus(self, *args):
        if not self.active:
            return

        if len(args) == 0 or args[0] is self:
            if self.parent:
                self.parent.focus(self)
            return

        if self.focus_child == args[0]:
            return

        if self.focus_child:
            self.focus_child.event(Event.focus_event(False))

        self.focus_child = args[0]

        if self.focus_child:
            self.focus_child.event(Event.focus_event(True))

    def has_focus(self):
        return self.active and not self.parent or self.parent.focus_child == self

    def window_bounds(self):
        min = Point(*self.window.getbegyx(), reversed=True)
        max = Point(*self.window.getmaxyx(), reversed=True)
        return (min, max)

    def window_bounds_hint(self, parent_bounds):
        return parent_bounds if not self.window else self.window_bounds()

    def loop(self):
        while True:
            self.render()
            self.get_input()

    def get_input(self):
        ch = self.window.getch()
        event = None

        if ch == curses.KEY_RESIZE:
            event = Event.resize_event(self.window_bounds());
        elif ch == curses.KEY_MOUSE:
            try:
                id, x, y, z, bstate = curses.getmouse()
                event = Event.mouse_event(Point(x, y), bstate)
            except curses.error:
                pass
        elif curses.ascii.isprint(ch):
            event = Event.text_event(chr(ch))
        else:
            event = Event.key_event(ch)

        if event is not None:
            self.event(event)

    def event(self, event):
        if event.type == Event.TYPE_RESIZE:
            self.resize_event(event)
            if event.propagate:
                bounds = self.window_bounds()
                for child in self.children:
                    old_bounds = child.window_bounds()
                    new_bounds = child.window_bounds_hint(bounds)
                    if old_bounds != new_bounds:
                        child.event(Event.resize_event(new_bounds))
            return

        if not self.active:
            return

        if event.type == Event.TYPE_TEXT:
            self.text_event(event)
            if self.focus_child and event.propagate:
                self.focus_child.event(event)
        elif event.type == Event.TYPE_KEY:
            self.key_event(event)
            if self.focus_child and event.propagate:
                self.focus_child.event(event)
        elif event.type == Event.TYPE_MOUSE:
            self.mouse_event(event)
            if not event.propagate:
                return
            for child in self.children:
                if child.active and event.pos.in_window(child.window):
                    if self.event_change_focus_child(child):
                        child_bounds = child.window_bounds()
                        relative = event.pos - child_bounds[0]
                        child_event = Event.mouse_event(relative, event.buttons)
                        child.event(child_event)
                        if not child_event.propagate:
                            return
        elif event.type == Event.TYPE_FOCUS:
            self.focus_event(event)

    def event_change_focus_child(self, new):
        self.focus_child = new
        return True

    def text_event(self, event):
        pass

    def key_event(self, event):
        pass

    def resize_event(self, event):
        self.adjust_window_size(event.bounds)

    def mouse_event(self, event):
        self.focus()

    def adjust_window_size(self, bounds):
        if self.window_bounds() != bounds:
            min, max = bounds
            size = max - min
            self.window.mvwin(min.y, min.x)
            self.window.resize(size.y, size.x)

    def refresh(self):
        self.window.clear()
        self.render()
        self.window.refresh()
        for child in self.children:
            if child.active:
                child.refresh()

    def render(self):
        pass

    def focus_event(self, event):
        pass


class Editor(Widget):
    def __init__(self, parent, window):
        super(Editor, self).__init__(parent, window)
        self.document = document.Document()
        self.active_layer = None
        self.file = ""
        self.cursor = Point()
        self.offset = Point(1, 1)
        self.message = ""

    def window_bounds_hint(self, parent_bounds):
        min, max = parent_bounds
        return (
            Point(min.x, min.y + 1),
            max
        )

    def open(self, file):
        self.document = document.loader.factory.load(file)
        self.file = file
        if self.document.layers:
            self.active_layer = self.document.layers[-1]
        else:
            self.active_layer = None

    def render(self):
        self.render_picture()
        self.render_ui()
        self.render_cursor()

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
        if self.has_focus():
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

    def text_event(self, event):
        self.set_char(event.char)
        self.cursor.x += 1
        self._adjust_cursor()

    def key_event(self, event):
        if event.key == curses.KEY_LEFT:
            self.cursor.x -= 1
        elif event.key == curses.KEY_RIGHT:
            self.cursor.x += 1
        elif event.key == curses.KEY_UP:
            self.cursor.y -= 1
        elif event.key == curses.KEY_DOWN or event.key == curses.KEY_ENTER:
            self.cursor.y += 1
        elif event.key == curses.KEY_HOME:
            self.cursor.x = 0
        elif event.key == curses.KEY_END:
            self.cursor.x = self.document.width
        elif event.key == curses.KEY_SHOME:
            self.cursor.y = 0
        elif event.key == curses.KEY_SEND:
            self.cursor.y = self.document.height
        elif event.key == curses.KEY_BACKSPACE:
            self.cursor.x -= 1
            self.set_char(" ") # TODO Remove the char
        elif event.key == curses.KEY_DC:
            self.set_char(" ") # TODO Remove the char
            self.cursor.x += 1
        self._adjust_cursor()
        event.accept()

    def resize_event(self, event):
        super(Editor, self).resize_event(event)
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

        self.refresh()

    @property
    def name(self):
        return self.document.name or os.path.basename(self.file)

    def mouse_event(self, event):
        super(Editor, self).mouse_event(event)
        if event.buttons == curses.BUTTON1_CLICKED:
            self.cursor = event.pos - self.offset
            event.accept()


class Manager(Widget):
    def __init__(self, window):
        super(Manager, self).__init__(None, window)
        self.editors = []
        self.current_editor = None
        curses.curs_set(0)

        height, width = self.window.getmaxyx()
        self.editor_window = curses.newwin(height-1, width, 1, 0)

        self.title_bar = HorizontalMenu(self, None, self.editors, None, lambda e: e.name)
        self.title_bar.signal_changed = self._switch_current_editor
        self.focus(self.title_bar)

    def open_tab(self, file=None):
        editor = Editor(self, self.editor_window)
        if file is not None:
            try:
                editor.open(file)
            except Exception:
                return
        self.editors.append(editor)
        self._switch_current_editor(self.editors[-1])
        self._activate_editor()

    def _switch_current_editor(self, editor):
        if editor != self.current_editor:

            old_editor = self.current_editor
            if old_editor:
                old_editor.active = False

            self.current_editor = editor
            self.title_bar.current = editor

            if editor:
                editor.active = True
                if self.focus_child == old_editor:
                    self.focus(editor)

            self.refresh()

    #def render(self):
        ##if self.current_editor and self.current_editor.has_focus():
        #self.current_editor.render()

    def _activate_editor(self):
        if self.current_editor:
            self.current_editor.active = True
            self.focus(self.current_editor)
            curses.curs_set(1)
            self.current_editor.refresh()

    def key_event(self, event):

        if event.key == 0x1b: # Escape
            if self.current_editor and self.current_editor.has_focus():
                self.focus(self.title_bar)
                curses.curs_set(0)
            else:
                self._activate_editor()
            self.refresh()
            event.accept()

        if self.current_editor and not self.current_editor.has_focus():
            if event.key == curses.KEY_UP:
                self._switch_layer(+1)
                event.accept()
            elif event.key == curses.KEY_DOWN:
                self._switch_layer(-1)
                event.accept()

    def _switch_layer(self, delta):
        if not self.current_editor or not self.current_editor.document.layers:
            return
        self.current_editor.active_layer = next_object(
            self.current_editor.document.layers,
            self.current_editor.active_layer,
            delta
        )
        self.current_editor.refresh()


class HorizontalMenu(Widget):
    def __init__(self, parent, window, items, current, formatter=str, separator="|"):
        super(HorizontalMenu, self).__init__(parent, window)
        self.items = items
        self.current = current
        self.formatter = formatter
        self.separator = separator
        self.signal_changed = lambda x: None
        self.render()

    def render(self):
        self.window.clear()
        x = 0
        self.window.addstr(0, x, self.separator)
        x += len(self.separator)
        for item in self.items:
            if item is not self.current:
                mode = curses.A_NORMAL
            elif self.has_focus():
                mode = curses.A_REVERSE
            else:
                mode = curses.A_UNDERLINE
            text = self.formatter(item)
            self.window.addstr(0, x, text, mode)
            x += len(text)
            self.window.addstr(0, x, self.separator)
            x += len(self.separator)
        self.window.refresh()
        # TODO handle overflow

    def key_event(self, event):
        if event.key == curses.KEY_LEFT:
            self._switch_element(-1)
        elif event.key == curses.KEY_RIGHT:
            self._switch_element(+1)

    def _switch_element(self, delta):
        if not self.items:
            return
        self.current = next_object(self.items, self.current, delta)
        self.signal_changed(self.current)
        self.render()

    def mouse_event(self, event):
        super(HorizontalMenu, self).mouse_event(event)

    def window_bounds_hint(self, parent_bounds):
        return (
            parent_bounds[0],
            Point(
                parent_bounds[1].x,
                parent_bounds[0].y + 1,
            )
        )


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
print manager.title_bar.window_bounds()
