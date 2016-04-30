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
import sys
import os
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from patsi.ansi import *


class TestAnsiCode(unittest.TestCase):
    def test_ctor(self):
        a = AnsiCode("m")
        self.assertEqual(a.terminator, "m")
        self.assertEqual(a.args(), [])
        self.assertEqual(a.private, "")

        a = AnsiCode("m", [1])
        self.assertEqual(a.terminator, "m")
        self.assertEqual(a.args(), [1])
        self.assertEqual(a.private, "")

        a = AnsiCode("m", [1], "?")
        self.assertEqual(a.terminator, "m")
        self.assertEqual(a.args(), [1])
        self.assertEqual(a.private, "?")

    def test_repr(self):
        a = AnsiCode("m", [1, 2, 3], "?")
        self.assertEqual(repr(a), "\x1b[?1;2;3m")

    def test_parse(self):
        tests = [
            "\x1b[K",
            "\x1b[1J",
            "\x1b[?25h",
            "\x1b[31;1m",
        ]
        for test in tests:
            a = AnsiCode.parse(test)
            self.assertTrue(isinstance(a, AnsiCode))
            self.assertEqual(repr(a), test)

    def test_split(self):
        split = list(AnsiCode.split("Hello\x1b[31mWorld\x1b[H\x1b[0mFoo"))
        self.assertEqual(split[0], "Hello")
        self.assertTrue(isinstance(split[1], AnsiCode))
        self.assertEqual(split[2], "World")
        self.assertTrue(isinstance(split[3], AnsiCode))
        self.assertTrue(isinstance(split[4], AnsiCode))
        self.assertEqual(split[5], "Foo")

    def test_compare(self):
        self.assertTrue(AnsiCode("m", ["1", "2", "3"]) ==
                        AnsiCode.parse("\x1b[1;2;3m"))

        self.assertTrue(AnsiCode("q", ["1", "2", "3"]) !=
                        AnsiCode.parse("\x1b[1;2;3m"))

        self.assertTrue(AnsiCode("m", ["1", "5", "3"]) !=
                        AnsiCode.parse("\x1b[1;2;3m"))

        self.assertTrue(AnsiCode("m", ["1", "2", "3"], "?") !=
                        AnsiCode.parse("\x1b[1;2;3m"))


class TestCursorPosition(unittest.TestCase):
    def test_parse(self):
        a = AnsiCode.parse("\x1b[3;4H")
        self.assertTrue(isinstance(a, CursorPosition))
        self.assertEqual(a.row, 3)
        self.assertEqual(a.column, 4)

        a = AnsiCode.parse("\x1b[3;4f")
        self.assertTrue(isinstance(a, CursorPosition))
        self.assertEqual(a.row, 3)
        self.assertEqual(a.column, 4)

        a = AnsiCode.parse("\x1b[H")
        self.assertTrue(isinstance(a, CursorPosition))
        self.assertEqual(a.row, 1)
        self.assertEqual(a.column, 1)

    def test_ctor(self):
        a = CursorPosition(3, 4)
        self.assertEqual(a.row, 4)
        self.assertEqual(a.column, 3)

        a = CursorPosition(x=3, y=4)
        self.assertEqual(a.row, 4)
        self.assertEqual(a.column, 3)

        a = CursorPosition(column=3, row=4)
        self.assertEqual(a.row, 4)
        self.assertEqual(a.column, 3)

        a = CursorPosition()
        self.assertEqual(a.row, 1)
        self.assertEqual(a.column, 1)

    def test_args(self):
        self.assertEqual(CursorPosition(row=3, column=4).args(), [3, 4])


class TestGraphicRendition(unittest.TestCase):
    def test_alias(self):
        self.assertEqual(SGR, GraphicRendition)

    def test_parse(self):
        a = AnsiCode.parse("\x1b[m")
        self.assertTrue(isinstance(a, GraphicRendition))
        self.assertEqual(a.flags, [])

        a = AnsiCode.parse("\x1b[1;2;3;4m")
        self.assertTrue(isinstance(a, GraphicRendition))
        self.assertEqual(a.flags, [1, 2, 3, 4])

    def test_ctor_simple(self):
        self.assertEqual(SGR().flags, [])
        self.assertEqual(SGR(1, 2, 3).flags, [1, 2, 3])
        self.assertEqual(SGR([1, 2, 3]).flags, [1, 2, 3])

    def test_ctor_color(self):
        a = SGR([31, 42, 93, 104])
        self.assertTrue(isinstance(a.flags[0], SGR.Color))
        self.assertEqual(a.flags[0].color, SGR.Color.Red)
        self.assertEqual(a.flags[0].background, False)
        self.assertEqual(a.flags[0].bright, False)
        self.assertEqual(repr(a.flags[0]), "31")

        self.assertTrue(isinstance(a.flags[1], SGR.Color))
        self.assertEqual(a.flags[1].color, SGR.Color.Green)
        self.assertEqual(a.flags[1].background, True)
        self.assertEqual(a.flags[1].bright, False)
        self.assertEqual(repr(a.flags[1]), "42")

        self.assertTrue(isinstance(a.flags[2], SGR.Color))
        self.assertEqual(a.flags[2].color, SGR.Color.Yellow)
        self.assertEqual(a.flags[2].background, False)
        self.assertEqual(a.flags[2].bright, True)
        self.assertEqual(repr(a.flags[2]), "93")

        self.assertTrue(isinstance(a.flags[3], SGR.Color))
        self.assertEqual(a.flags[3].color, SGR.Color.Blue)
        self.assertEqual(a.flags[3].background, True)
        self.assertEqual(a.flags[3].bright, True)
        self.assertEqual(repr(a.flags[3]), "104")

    def test_ctor_color256(self):
        a = SGR([38, 5, 69, 48, 5, 42])
        self.assertEqual(len(a.flags), 2)

        self.assertTrue(isinstance(a.flags[0], SGR.Color256))
        self.assertEqual(a.flags[0].color, 69)
        self.assertEqual(a.flags[0].background, False)
        self.assertEqual(repr(a.flags[0]), "38;5;69")

        self.assertTrue(isinstance(a.flags[1], SGR.Color256))
        self.assertEqual(a.flags[1].color, 42)
        self.assertEqual(a.flags[1].background, True)
        self.assertEqual(repr(a.flags[1]), "48;5;42")

    def test_ctor_color_rgb(self):
        a = SGR([38, 2, 1, 2, 3, 48, 2, 1, 2, 3])
        self.assertEqual(len(a.flags), 2)

        self.assertTrue(isinstance(a.flags[0], SGR.ColorRGB))
        self.assertEqual(a.flags[0].r, 1)
        self.assertEqual(a.flags[0].g, 2)
        self.assertEqual(a.flags[0].b, 3)
        self.assertEqual(a.flags[0].background, False)
        self.assertEqual(repr(a.flags[0]), "38;2;1;2;3")

        self.assertTrue(isinstance(a.flags[1], SGR.ColorRGB))
        self.assertEqual(a.flags[1].r, 1)
        self.assertEqual(a.flags[1].g, 2)
        self.assertEqual(a.flags[1].b, 3)
        self.assertEqual(a.flags[1].background, True)
        self.assertEqual(repr(a.flags[1]), "48;2;1;2;3")

    def test_background(self):
        color = SGR.Red
        bg = SGR.Background(color)
        self.assertEqual(bg.color, color.color)
        self.assertTrue(bg.background)
        self.assertFalse(color.background)

    def test_reverse(self):
        self.assertEqual(SGR.reverse(SGR.Bold), 22)
        self.assertEqual(SGR.reverse(SGR.Italic), 23)
        self.assertEqual(SGR.reverse(SGR.Underline), 24)
        self.assertEqual(SGR.reverse(31), 39)
        self.assertEqual(SGR.reverse(SGR.Red), 39)
        self.assertEqual(SGR.reverse(91), 39)
        self.assertEqual(SGR.reverse(SGR.Background(SGR.ColorRGB(1,2,3))), 49)
        self.assertEqual(SGR.reverse(1234), 0)

    def test_args(self):
        self.assertEqual(SGR([1, 2, 3]).args(), [1, 2, 3])

    def test_flag_values(self):
        pass


class TestCharMover(unittest.TestCase):
    def test_move(self):
        m = CharMover(0, 0)
        self.assertFalse(m.moved)
        m.move(2, 3)
        self.assertTrue(m.moved)
        self.assertEquals(m.x, 2)
        self.assertEquals(m.y, 3)

    def test_loop(self):
        m = CharMover(0, 0)
        string = "   ab\nc\td\re\vf"
        gen = m.loop(string)

        self.assertFalse(m.moved)
        self.assertEquals(next(gen), 'a')
        self.assertEquals((m.x, m.y), (3, 0))
        self.assertTrue(m.moved)

        self.assertEquals(next(gen), 'b')
        self.assertEquals((m.x, m.y), (4, 0))
        self.assertFalse(m.moved)

        self.assertEquals(next(gen), 'c')
        self.assertEquals((m.x, m.y), (0, 1))
        self.assertTrue(m.moved)

        self.assertEquals(next(gen), 'd')
        self.assertEquals((m.x, m.y), (5, 1))
        self.assertTrue(m.moved)

        self.assertEquals(next(gen), 'e')
        self.assertEquals((m.x, m.y), (0, 1))
        self.assertTrue(m.moved)

        self.assertEquals(next(gen), 'f')
        self.assertEquals((m.x, m.y), (2, 2))
        self.assertTrue(m.moved)


unittest.main()
