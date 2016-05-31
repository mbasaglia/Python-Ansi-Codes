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
import test_common

from patsi.ansi import *


class TestAnsiCode(test_common.TestCase):
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
        self.assertRaises(Exception, lambda: AnsiCode.parse("Foo"))

    def test_split(self):
        split = list(AnsiCode.split("Hello\x1b[31mWorld\x1b[H\x1b[0mFoo"))
        self.assertEqual(split[0], "Hello")
        self.assertTrue(isinstance(split[1], AnsiCode))
        self.assertEqual(split[2], "World")
        self.assertTrue(isinstance(split[3], AnsiCode))
        self.assertTrue(isinstance(split[4], AnsiCode))
        self.assertEqual(split[5], "Foo")
        self.assertEqual(list(AnsiCode.split("")), [])

    def test_compare(self):
        self.assertTrue(AnsiCode("m", ["1", "2", "3"]) ==
                        AnsiCode.parse("\x1b[1;2;3m"))

        self.assertTrue(AnsiCode("q", ["1", "2", "3"]) !=
                        AnsiCode.parse("\x1b[1;2;3m"))

        self.assertTrue(AnsiCode("m", ["1", "5", "3"]) !=
                        AnsiCode.parse("\x1b[1;2;3m"))

        self.assertTrue(AnsiCode("m", ["1", "2", "3"], "?") !=
                        AnsiCode.parse("\x1b[1;2;3m"))


class TestCursorPosition(test_common.TestCase):
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


class TestGraphicRendition(test_common.TestCase):
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
        self.assertEqual(SGR(1).flags, [1])

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

    def test_ctor_color_invalid(self):
        # TODO Is this the right behaviour or should it eat the mismatched flags?
        self.assertEqual(len(SGR([98, 5, 2, 3]).flags), 3)
        self.assertEqual(len(SGR([38, 2, 1]).flags), 2)
        self.assertEqual(len(SGR([48, 2, 1]).flags), 2)
        self.assertEqual(len(SGR([108, 2, 1]).flags), 2)

    def test_background(self):
        color = SGR.Red
        bg = SGR.Background(color)
        self.assertEqual(bg.color, color.color)
        self.assertTrue(bg.background)
        self.assertFalse(color.background)

    def test_reverse(self):
        reversible = [
            (SGR.Bold, 22),
            (SGR.Italic, 23),
            (SGR.Underline, 24),
        ]
        for a, b in reversible:
            self.assertEqual(SGR.reverse(a), b)
            self.assertEqual(SGR.reverse(b), a)
        self.assertEqual(SGR.reverse(41), 49)
        self.assertEqual(SGR.reverse(31), 39)
        self.assertEqual(SGR.reverse(SGR.Red), 39)
        self.assertEqual(SGR.reverse(91), 39)
        self.assertEqual(SGR.reverse(SGR.Background(SGR.ColorRGB(1,2,3))), 49)
        self.assertEqual(SGR.reverse(1234), 0)

    def test_args(self):
        self.assertEqual(SGR([1, 2, 3]).args(), [1, 2, 3])

    def test_flag_values(self):
        pass


class TestCharMover(test_common.TestCase):
    def test_move(self):
        m = CharMover(0, 0)
        self.assertFalse(m.moved)
        m.move(2, 3)
        self.assertTrue(m.moved)
        self.assertEqual(m.x, 2)
        self.assertEqual(m.y, 3)

    def test_loop(self):
        m = CharMover(0, 0)
        string = "   ab\nc\td\re\vf"
        gen = m.loop(string)

        self.assertFalse(m.moved)
        self.assertEqual(next(gen), 'a')
        self.assertEqual((m.x, m.y), (3, 0))
        self.assertTrue(m.moved)

        self.assertEqual(next(gen), 'b')
        self.assertEqual((m.x, m.y), (4, 0))
        self.assertFalse(m.moved)

        self.assertEqual(next(gen), 'c')
        self.assertEqual((m.x, m.y), (0, 1))
        self.assertTrue(m.moved)

        self.assertEqual(next(gen), 'd')
        self.assertEqual((m.x, m.y), (5, 1))
        self.assertTrue(m.moved)

        self.assertEqual(next(gen), 'e')
        self.assertEqual((m.x, m.y), (0, 1))
        self.assertTrue(m.moved)

        self.assertEqual(next(gen), 'f')
        self.assertEqual((m.x, m.y), (2, 2))
        self.assertTrue(m.moved)


class TestAnsiRenderer(test_common.StringOutputTestCase):
    def setUp(self):
        super(TestAnsiRenderer, self).setUp()
        self.renderer = AnsiRenderer(self.output)

    def test_ctor(self):
        self.assertIs(self.renderer.output, self.output)

    def test_context_nocursor(self):
        with self.renderer.context_nocursor():
            self._check_data(common.hide_cursor)
            self._clear_data()
        self._check_data(common.show_cursor)

    def test_context_alt_screen(self):
        with self.renderer.context_alt_screen():
            self._check_data(common.alt_screen)
            self._clear_data()
        self._check_data(common.main_screen)

    def test_context_sgr(self):
        self.renderer.ansi(SGR(SGR.Bold))
        with self.renderer.context_sgr(SGR.Underline):
            self._check_data(SGR(SGR.Bold), SGR(SGR.Underline))
        self._check_data(SGR(SGR.Bold), SGR(SGR.Underline), SGR(SGR.reverse(SGR.Underline)))

        self._clear_data()
        self.renderer.ansi(SGR(SGR.Bold))
        with self.renderer.context_sgr(SGR.Underline, hard_reset=True):
            self._check_data(SGR(SGR.Bold), SGR(SGR.Underline))
        self._check_data(SGR(SGR.Bold), SGR(SGR.Underline), SGR(0))

    def test_rendering_context(self):
        with self.renderer.rendering_context():
            self._check_data(common.alt_screen, common.hide_cursor,
                             common.clear_screen, SGR(SGR.Reset))
            self._clear_data()
            raise KeyboardInterrupt
        self._check_data(common.show_cursor, common.main_screen)

    def test_keyboard_interrupt(self):
        with keyboard_interrupt():
            raise KeyboardInterrupt
        self.assertTrue(True)

    def test_ansi(self):
        self.renderer.ansi(SGR(SGR.Bold))
        self._check_data(SGR(SGR.Bold))

        self._clear_data()
        self.renderer.ansi("m", [1])
        self._check_data(SGR(SGR.Bold))

    def test_move_cursor(self):
        self.renderer.move_cursor(2, 3)
        self._check_data(CursorPosition(2, 3))

        self._clear_data()
        self.renderer.move_cursor()
        self._check_data(CursorPosition())

    def test_clear(self):
        self.renderer.clear()
        self._check_data(common.clear_screen)

    def test_write(self):
        self.renderer.write("Hello")
        self.assertEqual(self.output.getvalue(), "Hello")

    def test_overlay(self):
        self.renderer.overlay("abc\nd\x1b[31me")
        self.assertEqual(self.output.getvalue(), "abc\x1b[2;1Hd\x1b[31me")


test_common.main()
