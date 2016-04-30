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
from StringIO import StringIO

from . import factory
from .ansi import AnsiFormatter


_default_replacements = {
    "\n": "\\n",
    "\"": "\\\"",
    "\\": "\\\\",
    "\x1b": "\\x1b",
}


class AnsiSourceFormatter(object):
    flat = True

    def __init__(self, prefix='"', suffix='"\n',
                 replacements=_default_replacements, *args, **kwargs):
        self.prefix = prefix
        self.suffix = suffix
        self._ansi_formatter = AnsiFormatter(*args, **kwargs)
        self._repl_dict = replacements
        self._repl_search = re.compile("|".join(map(re.escape, replacements.keys())))
        self._repl_replace = lambda match: self._repl_dict[match.group()]

    def _wrap_ansi(self, func, object, output):
        output.write(self.prefix)
        buffer = StringIO()
        func(object, buffer)
        output.write(self._replace(buffer.getvalue()))
        output.write(self.suffix)

    def _replace(self, string):
        return self._repl_search.sub(self._repl_replace, string)

    def document(self, doc, output):
        self._wrap_ansi(self._ansi_formatter.document, doc, output)

    def layer(self, layer, output):
        self._wrap_ansi(self._ansi_formatter.layer, layer, output)

    def color(self, color):
        return self.prefix + self._replace(self._ansi_formatter(color)) + \
            self.suffix

AnsiSourceFormatter.builtins = {
    "bash": AnsiSourceFormatter(
        "#!/bin/bash\nread -r -d '' Heredoc_var <<'Heredoc_var'\n\\x1b[0m",
        "\\x1b[0m\nHeredoc_var\necho -e \"$Heredoc_var\"\n",
        {"\\": "\\\\", "\x1b": "\\x1b"}
    ),
    "python": AnsiSourceFormatter(
        "print('''",
        "''')\n",
        {"\\": "\\\\", "\'": "\\\'", "\x1b": "\\x1b"}
    ),
    "perl": AnsiSourceFormatter(
        "print \"",
        "\";\n",
        {"\\": "\\\\", "\"": "\\\"", "\x1b": "\\x1b",
         "$": "\\$", "@": "\\@", "%": "\\%"}
    ),
    "php": AnsiSourceFormatter(
        "<?php\nprint \"",
        "\";\n",
        {"\\": "\\\\", "\"": "\\\"", "\x1b": "\\x1b", "$": "\\$"}
    ),
}


factory.register(AnsiSourceFormatter.builtins["bash"], "sh")
factory.register(AnsiSourceFormatter.builtins["python"], "py")
factory.register(AnsiSourceFormatter.builtins["perl"], "pl")
factory.register(AnsiSourceFormatter.builtins["php"], "php")
