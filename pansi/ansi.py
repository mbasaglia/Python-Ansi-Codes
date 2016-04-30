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
import sys
import copy
from contextlib import contextmanager


class AnsiCode(object):
    """
    Class representing an ANSI code.

    This class supports a subset of the codes with the
    Control Sequence Introducer
    """

    CSI = "\x1b["
    CSI_PATTERN = re.compile("\x1b\[([<-?]?)([0-9;]*)([@-~])")

    def __init__(self, terminator, args=[], private=""):
        self.terminator = terminator
        self._args = args
        self.private = private

    def __repr__(self):
        """
        Returns the ANSI-encoded string for this code
        """
        return (AnsiCode.CSI + self.private +
                ";".join(str(arg) for arg in self.args()) +
                self.terminator)

    def args(self):
        """
        List of arguments to the ANSI code, as a function to allow overriding
        """
        return self._args

    @staticmethod
    def parse(string):
        """
        Parses an ANSI code string into an object
        """
        match = AnsiCode.CSI_PATTERN.match(string)
        if not match:
            raise Exception(
                "Not a valid escape sequence: %s" %
                string.replace("\x1b", "\\e")
            )
        return AnsiCode._from_match(match)

    @staticmethod
    def _from_match(match):
        """
        Converts a regex match (matched from CSI_PATTERN) into a code object
        """
        letter = match.group(3)
        args = filter(bool, match.group(2).split(";"))
        private = match.group(1)
        if (letter == 'H' or letter == 'f') and not private:
            return CursorPosition(
                row=int(args[0]) if len(args) > 0 else 1,
                column=int(args[1]) if len(args) > 1 else 1
            )
        elif letter == 'm' and not private:
            return GraphicRendition(int(arg) for arg in args)
        else:
            return AnsiCode(letter, args, private)

    @staticmethod
    def split(string):
        """
        Generator that splits a string into a list.
        Each element can either be a simple string or an AnsiCode object
        """
        while string:
            match = AnsiCode.CSI_PATTERN.search(string)
            if not match:
                yield string
                break
            if match.start():
                yield string[:match.start()]
            yield AnsiCode._from_match(match)
            string = string[match.end():]

    def __eq__(self, other):
        return repr(self) == repr(other)

    def __ne__(self, other):
        return not (self == other)


class CursorPosition(AnsiCode):
    """
    Class representing a CUP (Cursor position) code.

    Coordinates are 1-indexed.
    """
    def __init__(self, *args, **kwargs):
        AnsiCode.__init__(self, "H")
        if "x" in kwargs and "y" in kwargs:
            self.column = kwargs["x"]
            self.row = kwargs["y"]
        elif "column" in kwargs and "row" in kwargs:
            self.column = kwargs["column"]
            self.row = kwargs["row"]
        elif len(args) == 2:
            self.column = args[0]
            self.row = args[1]
        else:
            self.column = self.row = 1

    def args(self):
        return [self.row, self.column]


class GraphicRendition(AnsiCode):
    """
    Class representing a SGR (Select Graphic Rendition) code.
    """
    Reset       = 0 # Flag to reset all formatting
    Bold        = 1
    Italic      = 3
    Underline   = 4
    Blink       = 5
    Negative    = 7

    class Color(object):
        """
        Class representing an indexed color (8 colors).

        Bright colors result into the non-standard 90 group.
        """
        Black   = 0
        Red     = 1
        Green   = 2
        Yellow  = Red | Green
        Blue    = 4
        Magenta = Blue | Red
        Cyan    = Blue | Green
        White   = Red | Green | Blue
        ResetColor = 9

        def __init__(self, color=ResetColor, background=False, bright=False):
            self.color = color
            self.background = background
            self.bright = bright

        def __repr__(self):
            base = 30
            if self.bright and self.color != GraphicRendition.Color.ResetColor:
                base = 90
            if self.background:
                base += 10
            base += self.color
            return str(base)

    class Color256(object):
        """
        Class representing a non-standard indexed color (256 colors)
        """
        def __init__(self, index, background=False):
            self.color = index
            self.background = background

        def __repr__(self):
            base = 4 if self.background else 3
            return "%s8;5;%s" % (base, self.color)

    class ColorRGB(object):
        """
        Class representing a non-standard 24bit RGB color
        """
        def __init__(self, r, g, b, background=False):
            self.r = r
            self.g = g
            self.b = b
            self.background = background

        def __repr__(self):
            base = 4 if self.background else 3
            return "%s8;2;%s;%s;%s" % (base, self.r, self.g, self.b)

    @staticmethod
    def Background(color):
        """
        Turns a color object into a background color
        """
        bg = copy.copy(color)
        bg.background = True
        return bg

    def __init__(self, *args):
        AnsiCode.__init__(self, "m")

        def _issequence(x):
            try:
                iter(x)
                return True
            except:
                return False

        if len(args) == 1 and _issequence(args[0]):
            flags = list(args[0])
        else:
            flags = list(args)

        def pop_color(index, flags, background, bright):
            if index == 8:
                if bright:
                    return None
                if len(flags) >= 2 and flags[0] == 5:
                    flags.pop(0)
                    return GraphicRendition.Color256(flags.pop(0), background)
                if len(flags) >= 4 and flags[0] == 2:
                    args = flags[1:4] + [background]
                    flags.pop(0)
                    flags.pop(0)
                    flags.pop(0)
                    flags.pop(0)
                    return GraphicRendition.ColorRGB(*args)
                return None
            else:
                return GraphicRendition.Color(index, background, bright)

        self.flags = []

        while flags:
            flag = flags.pop(0)
            if flag >= 30 and flag < 40:
                color = pop_color(flag % 10, flags, False, False)
                if color:
                    self.flags.append(color)
            elif flag >= 40 and flag < 50:
                color = pop_color(flag % 10, flags, True, False)
                if color:
                    self.flags.append(color)
            elif flag >= 90 and flag < 100:
                color = pop_color(flag % 10, flags, False, True)
                if color:
                    self.flags.append(color)
            elif flag >= 100 and flag < 110:
                color = pop_color(flag % 10, flags, True, True)
                if color:
                    self.flags.append(color)
            else:
                self.flags.append(flag)

    @staticmethod
    def reverse(flag):
        """
        Returns a flag that undoes the given one
        """
        if type(flag) is not int:
            if flag.background:
                return 49
            return 39
        elif flag == 1:
            return 22
        elif flag == 22:
            return 1
        elif flag in xrange(1, 10):
            return 20 + flag
        elif flag in xrange(21, 30):
            return flag - 20
        elif flag in xrange(30, 40) or flag in xrange(90, 100):
            return 39
        elif flag in xrange(40, 50) or flag in xrange(100, 110):
            return 49
        return 0

    def args(self):
        return self.flags

    class _Meta(type):
        """
        Sets up shortcuts to access standard colors
        """
        @staticmethod
        def __new__(meta, name, bases, dct):
            cls = type.__new__(meta, name, bases, dct)
            for name, value in vars(cls.Color).iteritems():
                if name[0].isupper():
                    setattr(cls, name, cls.Color(value))
            return cls
    __metaclass__ = _Meta


# Shorthand for GraphicRendition
SGR = GraphicRendition


# TODO Make this a module
class common(object):
    hide_cursor  = AnsiCode("l", [25], "?")
    show_cursor  = AnsiCode("h", [25], "?")
    alt_screen   = AnsiCode("h", [47], "?")
    main_screen  = AnsiCode("l", [47], "?")
    clear_screen = AnsiCode("J", [2])


class AnsiRenderer(object):
    """
    Class with a simplified interface to render ANSI codes to a file object
    """

    def __init__(self, output=sys.stdout):
        self.output = output

    @contextmanager
    def context_nocursor(self):
        """
        Context manager that disables the text cursor
        """
        self.ansi(common.hide_cursor)
        try:
            yield
        finally:
            self.ansi(common.show_cursor)

    @contextmanager
    def context_alt_screen(self):
        """
        Context manager that switch to an alternate screen
        """
        self.ansi(common.alt_screen)
        try:
            yield
        finally:
            self.ansi(common.main_screen)

    @contextmanager
    def context_sgr(self, *args, **kwargs):
        """
        Context manager that changes the formatting

        with hard_reset clears all formatting on exit
        """
        sgr = SGR(*args)
        hard_reset = kwargs.pop("hard_reset", False)
        self.ansi(sgr)
        try:
            yield
        finally:
            if hard_reset:
                self.ansi(SGR(SGR.Reset))
            else:
                self.ansi(SGR([SGR.reverse(flag) for flag in sgr.flags]))

    @contextmanager
    def rendering_context(self):
        """
        Context manager for a clean rendering environment
        """
        with keyboard_interrupt(), self.context_alt_screen(), self.context_nocursor():
            self.clear()
            self.ansi(SGR(SGR.Reset))
            yield

    def ansi(self, *args, **kwargs):
        """
        Prints an ANSI code to the output
        """
        if not kwargs and len(args) == 1 and isinstance(args[0], AnsiCode):
            code = args[0]
        else:
            code = AnsiCode(*args, **kwargs)
        self.output.write(str(code))
        self.output.flush()

    def move_cursor(self, *args, **kwargs):
        """
        Moves the cursor to the given coordinates
        """
        self.ansi(CursorPosition(*args, **kwargs))

    def clear(self):
        """
        Clears the screen
        """
        self.ansi(common.clear_screen)

    def write(self, *args):
        """
        Writes some text
        """
        self.output.write(" ".join(str(arg) for arg in args))
        self.output.flush()

    def overlay(self, string, start_x=1, start_y=1, tab_width=4):
        """
        Overlays string at the given position

        Space characters are converted into cursor movement, so they will not
        overwrite existing characters, ANSI codes from the strings are preserved
        (They must be in the subset that AnsiCode can parse)
        """
        x = start_x
        y = start_y
        for item in AnsiCode.split(string):
            if isinstance(item, AnsiCode):
                self.ansi(item)
            else:
                mover = CharMover(start_x, start_y)
                mover.move(x, y, False)
                for ch in mover.loop(string):
                    if mover.moved:
                        self.move_cursor(x, y)
                    self.output.write(ch)
                x = mover.x
                y = mover.y
        self.output.flush()


class CharMover(object):
    def __init__(self, start_x, start_y, tab_width=4):
        self.x = self.start_x = start_x
        self.y = self.start_y = start_y
        self.tab_width = tab_width
        self.moved = False

    def move(self, x, y, moved=True):
        self.x = x
        self.y = y
        self.moved = moved or self.moved

    def loop(self, string):
        for ch in string:
            if ch == ' ':
                self.x += 1
                self.moved = True
            elif ch == '\n':
                self.x = self.start_x
                self.y += 1
                self.moved = True
            elif ch == '\v':
                self.x += 1
                self.y += 1
                self.moved = True
            elif ch == '\r':
                self.x = self.start_x
                self.moved = True
            elif ch == '\t':
                self.x += self.tab_width
                self.moved = True
            else:
                yield ch
                self.moved = False
                self.x += 1


@contextmanager
def keyboard_interrupt():
    """
    Context manager that exits cleanly on KeyboardInterrupt
    """
    try:
        yield
    except KeyboardInterrupt:
        pass
