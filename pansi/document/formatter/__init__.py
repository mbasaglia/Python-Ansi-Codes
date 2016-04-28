from .ansi import AnsiFormatter
from .text import TextFormatter
from .svg import SvgFormatter
from .irc import IrcFormatter
try:
    from .png import PngFormatter
except ImportError:
    pass
