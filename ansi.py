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
    CSI_PATTERN = re.compile("\x1b\[([<-?])([0-9;]*)([@-~])")

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
            raise Exception("Not a valid escape sequence")
        return AnsiCode._from_match(match)

    @staticmethod
    def _from_match(match):
        """
        Converts a regex match (matched from CSI_PATTERN) into a code object
        """
        return AnsiCode(match.group(3), match.group(2).split(";"), match.group(1))

    @staticmethod
    def split(string):
        """
        Generator that splits a string into a list.
        Each element can either be a simple string or an AnsiCode object
        """
        result = []
        while string:
            match = AnsiCode.CSI_PATTERN.search(string)
            if not match:
                yield string
                break
            if match.start():
                yield string[:match.start()]
            yield AnsiCode._from_match(match)
            string = string[match.end():]


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
        if "column" in kwargs and "row" in kwargs:
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
        Yellow  = Red|Green
        Blue    = 4
        Magenta = Blue|Red
        Cyan    = Blue|Green
        White   = Red|Green|Blue
        ResetColor = 9

        def __init__(self, color=ResetColor, background=False, bright=False):
            self.color = color
            self.background = background
            self.bright = bright

        def __repr__(self):
            base = 30
            if self.bright and self.color != reset:
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
        if len(args) == 1 and type(args[0]) is list:
            self.flags = args[0]
        else:
            self.flags = args

    @staticmethod
    def reverse(flag):
        """
        Returns a flag that undoes the given one
        """
        if flag == 1:
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
        self.ansi("l", [25], "?")
        try:
            yield
        finally:
            self.ansi("h", [25], "?")

    @contextmanager
    def context_alt_screen(self):
        """
        Context manager that switch to an alternate screen
        """
        self.ansi("h", [47], "?")
        try:
            yield
        finally:
            self.ansi("l", [47], "?")

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
        self.ansi("J", [2])

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
        dirty_pos = False
        for item in AnsiCode.split(string):
            if isinstance(item, AnsiCode):
                self.ansi(item)
            else:
                for ch in string:
                    if ch == ' ':
                        x += 1
                        dirty_pos = True
                    elif ch == '\n':
                        x = start_x
                        y += 1
                        dirty_pos = True
                    elif ch == '\v':
                        x += 1
                        y += 1
                        dirty_pos = True
                    elif ch == '\r':
                        x = start_x
                        dirty_pos = True
                    elif ch == '\t':
                        x += tab_width
                        dirty_pos = True
                    else:
                        if dirty_pos:
                            self.move_cursor(x, y)
                            dirty_pos = False
                        self.output.write(ch)
                        x += 1
        self.output.flush()


@contextmanager
def keyboard_interrupt():
    """
    Context manager that exits cleanly on KeyboardInterrupt
    """
    try:
        yield
    except KeyboardInterrupt:
        pass
