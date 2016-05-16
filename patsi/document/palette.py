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
import copy
from . import color


class Palette(object):
    def __init__(self, *args):
        if len(args) == 1:
            colors = list(args[0])
        else:
            colors = args

        self.names = [color[0] for color in colors]
        self.colors = [color[1] for color in colors]

    def rgb_tuple(self, index):
        return self.colors[index]

    def name(self, index):
        return self.names[index]

    def rgb(self, index):
        return color.RgbColor(
            self.colors[index][0],
            self.colors[index][1],
            self.colors[index][2],
            self.names[index]
        )

    def find_index(self, value):
        if type(value) is tuple:
            return self.colors.index(value)
        return self.names.index(value)

    def __iter__(self):
        for item in zip(self.names, self.colors):
            yield item

    def __iadd__(self, other):
        for name, color in other:
            if name in self.names:
                self.colors[self.names.index(name)] = color
            else:
                self.names.append(name)
                self.colors.append(color)
        return self

    def __len__(self):
        return len(self.colors)

    def __add__(self, other):
        temp = copy.deepcopy(self)
        temp += other
        return temp


colors8_dark = Palette(
    ("black",    (0, 0, 0)),
    ("red",      (178, 24, 24)),
    ("green",    (24, 178, 24)),
    ("yellow",   (178, 104, 24)),
    ("blue",     (59, 59, 255)),
    ("magenta",  (178, 24, 178)),
    ("cyan",     (24, 178, 178)),
    ("white",    (178, 178, 178))
)

colors8_bright = Palette(
    ("black",    (104, 104, 104)),
    ("red",      (255, 84, 84)),
    ("green",    (84, 255, 84)),
    ("yellow",   (214, 214, 70)),
    ("blue",     (84, 84, 255)),
    ("magenta",  (255, 84, 255)),
    ("cyan",     (84, 255, 255)),
    ("white",    (255, 255, 255))
)
colors8_bright.bright = True

colors16 = colors8_dark + Palette(
    ("%s_bright" % name, value)
    for name, value in colors8_bright
)

colors256 = Palette([
    ("Black", (0, 0, 0)),
    ("Maroon", (128, 0, 0)),
    ("Green", (0, 0, 128)),
    ("Olive", (128, 0, 128)),
    ("Navy", (0, 128, 0)),
    ("Purple", (128, 128, 0)),
    ("Teal", (0, 128, 128)),
    ("Silver", (192, 192, 192)),
    ("Grey", (128, 128, 128)),
    ("Red", (255, 0, 0)),
    ("Lime", (0, 0, 255)),
    ("Yellow", (255, 0, 255)),
    ("Blue", (0, 255, 0)),
    ("Fuchsia", (255, 255, 0)),
    ("Aqua", (0, 255, 255)),
    ("White", (255, 255, 255)),
    ("Grey0", (0, 0, 0)),
    ("NavyBlue", (0, 95, 0)),
    ("DarkBlue", (0, 135, 0)),
    ("Blue3", (0, 175, 0)),
    ("Blue3", (0, 215, 0)),
    ("Blue1", (0, 255, 0)),
    ("DarkGreen", (0, 0, 95)),
    ("DeepSkyBlue4", (0, 95, 95)),
    ("DeepSkyBlue4", (0, 135, 95)),
    ("DeepSkyBlue4", (0, 175, 95)),
    ("DodgerBlue3", (0, 215, 95)),
    ("DodgerBlue2", (0, 255, 95)),
    ("Green4", (0, 0, 135)),
    ("SpringGreen4", (0, 95, 135)),
    ("Turquoise4", (0, 135, 135)),
    ("DeepSkyBlue3", (0, 175, 135)),
    ("DeepSkyBlue3", (0, 215, 135)),
    ("DodgerBlue1", (0, 255, 135)),
    ("Green3", (0, 0, 175)),
    ("SpringGreen3", (0, 95, 175)),
    ("DarkCyan", (0, 135, 175)),
    ("LightSeaGreen", (0, 175, 175)),
    ("DeepSkyBlue2", (0, 215, 175)),
    ("DeepSkyBlue1", (0, 255, 175)),
    ("Green3", (0, 0, 215)),
    ("SpringGreen3", (0, 95, 215)),
    ("SpringGreen2", (0, 135, 215)),
    ("Cyan3", (0, 175, 215)),
    ("DarkTurquoise", (0, 215, 215)),
    ("Turquoise2", (0, 255, 215)),
    ("Green1", (0, 0, 255)),
    ("SpringGreen2", (0, 95, 255)),
    ("SpringGreen1", (0, 135, 255)),
    ("MediumSpringGreen", (0, 175, 255)),
    ("Cyan2", (0, 215, 255)),
    ("Cyan1", (0, 255, 255)),
    ("DarkRed", (95, 0, 0)),
    ("DeepPink4", (95, 95, 0)),
    ("Purple4", (95, 135, 0)),
    ("Purple4", (95, 175, 0)),
    ("Purple3", (95, 215, 0)),
    ("BlueViolet", (95, 255, 0)),
    ("Orange4", (95, 0, 95)),
    ("Grey37", (95, 95, 95)),
    ("MediumPurple4", (95, 135, 95)),
    ("SlateBlue3", (95, 175, 95)),
    ("SlateBlue3", (95, 215, 95)),
    ("RoyalBlue1", (95, 255, 95)),
    ("Chartreuse4", (95, 0, 135)),
    ("DarkSeaGreen4", (95, 95, 135)),
    ("PaleTurquoise4", (95, 135, 135)),
    ("SteelBlue", (95, 175, 135)),
    ("SteelBlue3", (95, 215, 135)),
    ("CornflowerBlue", (95, 255, 135)),
    ("Chartreuse3", (95, 0, 175)),
    ("DarkSeaGreen4", (95, 95, 175)),
    ("CadetBlue", (95, 135, 175)),
    ("CadetBlue", (95, 175, 175)),
    ("SkyBlue3", (95, 215, 175)),
    ("SteelBlue1", (95, 255, 175)),
    ("Chartreuse3", (95, 0, 215)),
    ("PaleGreen3", (95, 95, 215)),
    ("SeaGreen3", (95, 135, 215)),
    ("Aquamarine3", (95, 175, 215)),
    ("MediumTurquoise", (95, 215, 215)),
    ("SteelBlue1", (95, 255, 215)),
    ("Chartreuse2", (95, 0, 255)),
    ("SeaGreen2", (95, 95, 255)),
    ("SeaGreen1", (95, 135, 255)),
    ("SeaGreen1", (95, 175, 255)),
    ("Aquamarine1", (95, 215, 255)),
    ("DarkSlateGray2", (95, 255, 255)),
    ("DarkRed", (135, 0, 0)),
    ("DeepPink4", (135, 95, 0)),
    ("DarkMagenta", (135, 135, 0)),
    ("DarkMagenta", (135, 175, 0)),
    ("DarkViolet", (135, 215, 0)),
    ("Purple", (135, 255, 0)),
    ("Orange4", (135, 0, 95)),
    ("LightPink4", (135, 95, 95)),
    ("Plum4", (135, 135, 95)),
    ("MediumPurple3", (135, 175, 95)),
    ("MediumPurple3", (135, 215, 95)),
    ("SlateBlue1", (135, 255, 95)),
    ("Yellow4", (135, 0, 135)),
    ("Wheat4", (135, 95, 135)),
    ("Grey53", (135, 135, 135)),
    ("LightSlateGrey", (135, 175, 135)),
    ("MediumPurple", (135, 215, 135)),
    ("LightSlateBlue", (135, 255, 135)),
    ("Yellow4", (135, 0, 175)),
    ("DarkOliveGreen3", (135, 95, 175)),
    ("DarkSeaGreen", (135, 135, 175)),
    ("LightSkyBlue3", (135, 175, 175)),
    ("LightSkyBlue3", (135, 215, 175)),
    ("SkyBlue2", (135, 255, 175)),
    ("Chartreuse2", (135, 0, 215)),
    ("DarkOliveGreen3", (135, 95, 215)),
    ("PaleGreen3", (135, 135, 215)),
    ("DarkSeaGreen3", (135, 175, 215)),
    ("DarkSlateGray3", (135, 215, 215)),
    ("SkyBlue1", (135, 255, 215)),
    ("Chartreuse1", (135, 0, 255)),
    ("LightGreen", (135, 95, 255)),
    ("LightGreen", (135, 135, 255)),
    ("PaleGreen1", (135, 175, 255)),
    ("Aquamarine1", (135, 215, 255)),
    ("DarkSlateGray1", (135, 255, 255)),
    ("Red3", (175, 0, 0)),
    ("DeepPink4", (175, 95, 0)),
    ("MediumVioletRed", (175, 135, 0)),
    ("Magenta3", (175, 175, 0)),
    ("DarkViolet", (175, 215, 0)),
    ("Purple", (175, 255, 0)),
    ("DarkOrange3", (175, 0, 95)),
    ("IndianRed", (175, 95, 95)),
    ("HotPink3", (175, 135, 95)),
    ("MediumOrchid3", (175, 175, 95)),
    ("MediumOrchid", (175, 215, 95)),
    ("MediumPurple2", (175, 255, 95)),
    ("DarkGoldenrod", (175, 0, 135)),
    ("LightSalmon3", (175, 95, 135)),
    ("RosyBrown", (175, 135, 135)),
    ("Grey63", (175, 175, 135)),
    ("MediumPurple2", (175, 215, 135)),
    ("MediumPurple1", (175, 255, 135)),
    ("Gold3", (175, 0, 175)),
    ("DarkKhaki", (175, 95, 175)),
    ("NavajoWhite3", (175, 135, 175)),
    ("Grey69", (175, 175, 175)),
    ("LightSteelBlue3", (175, 215, 175)),
    ("LightSteelBlue", (175, 255, 175)),
    ("Yellow3", (175, 0, 215)),
    ("DarkOliveGreen3", (175, 95, 215)),
    ("DarkSeaGreen3", (175, 135, 215)),
    ("DarkSeaGreen2", (175, 175, 215)),
    ("LightCyan3", (175, 215, 215)),
    ("LightSkyBlue1", (175, 255, 215)),
    ("GreenYellow", (175, 0, 255)),
    ("DarkOliveGreen2", (175, 95, 255)),
    ("PaleGreen1", (175, 135, 255)),
    ("DarkSeaGreen2", (175, 175, 255)),
    ("DarkSeaGreen1", (175, 215, 255)),
    ("PaleTurquoise1", (175, 255, 255)),
    ("Red3", (215, 0, 0)),
    ("DeepPink3", (215, 95, 0)),
    ("DeepPink3", (215, 135, 0)),
    ("Magenta3", (215, 175, 0)),
    ("Magenta3", (215, 215, 0)),
    ("Magenta2", (215, 255, 0)),
    ("DarkOrange3", (215, 0, 95)),
    ("IndianRed", (215, 95, 95)),
    ("HotPink3", (215, 135, 95)),
    ("HotPink2", (215, 175, 95)),
    ("Orchid", (215, 215, 95)),
    ("MediumOrchid1", (215, 255, 95)),
    ("Orange3", (215, 0, 135)),
    ("LightSalmon3", (215, 95, 135)),
    ("LightPink3", (215, 135, 135)),
    ("Pink3", (215, 175, 135)),
    ("Plum3", (215, 215, 135)),
    ("Violet", (215, 255, 135)),
    ("Gold3", (215, 0, 175)),
    ("LightGoldenrod3", (215, 95, 175)),
    ("Tan", (215, 135, 175)),
    ("MistyRose3", (215, 175, 175)),
    ("Thistle3", (215, 215, 175)),
    ("Plum2", (215, 255, 175)),
    ("Yellow3", (215, 0, 215)),
    ("Khaki3", (215, 95, 215)),
    ("LightGoldenrod2", (215, 135, 215)),
    ("LightYellow3", (215, 175, 215)),
    ("Grey84", (215, 215, 215)),
    ("LightSteelBlue1", (215, 255, 215)),
    ("Yellow2", (215, 0, 255)),
    ("DarkOliveGreen1", (215, 95, 255)),
    ("DarkOliveGreen1", (215, 135, 255)),
    ("DarkSeaGreen1", (215, 175, 255)),
    ("Honeydew2", (215, 215, 255)),
    ("LightCyan1", (215, 255, 255)),
    ("Red1", (255, 0, 0)),
    ("DeepPink2", (255, 95, 0)),
    ("DeepPink1", (255, 135, 0)),
    ("DeepPink1", (255, 175, 0)),
    ("Magenta2", (255, 215, 0)),
    ("Magenta1", (255, 255, 0)),
    ("OrangeRed1", (255, 0, 95)),
    ("IndianRed1", (255, 95, 95)),
    ("IndianRed1", (255, 135, 95)),
    ("HotPink", (255, 175, 95)),
    ("HotPink", (255, 215, 95)),
    ("MediumOrchid1", (255, 255, 95)),
    ("DarkOrange", (255, 0, 135)),
    ("Salmon1", (255, 95, 135)),
    ("LightCoral", (255, 135, 135)),
    ("PaleVioletRed1", (255, 175, 135)),
    ("Orchid2", (255, 215, 135)),
    ("Orchid1", (255, 255, 135)),
    ("Orange1", (255, 0, 175)),
    ("SandyBrown", (255, 95, 175)),
    ("LightSalmon1", (255, 135, 175)),
    ("LightPink1", (255, 175, 175)),
    ("Pink1", (255, 215, 175)),
    ("Plum1", (255, 255, 175)),
    ("Gold1", (255, 0, 215)),
    ("LightGoldenrod2", (255, 95, 215)),
    ("LightGoldenrod2", (255, 135, 215)),
    ("NavajoWhite1", (255, 175, 215)),
    ("MistyRose1", (255, 215, 215)),
    ("Thistle1", (255, 255, 215)),
    ("Yellow1", (255, 0, 255)),
    ("LightGoldenrod1", (255, 95, 255)),
    ("Khaki1", (255, 135, 255)),
    ("Wheat1", (255, 175, 255)),
    ("Cornsilk1", (255, 215, 255)),
    ("Grey100", (255, 255, 255)),
    ("Grey3", (8, 8, 8)),
    ("Grey7", (18, 18, 18)),
    ("Grey11", (28, 28, 28)),
    ("Grey15", (38, 38, 38)),
    ("Grey19", (48, 48, 48)),
    ("Grey23", (58, 58, 58)),
    ("Grey27", (68, 68, 68)),
    ("Grey30", (78, 78, 78)),
    ("Grey35", (88, 88, 88)),
    ("Grey39", (98, 98, 98)),
    ("Grey42", (108, 108, 108)),
    ("Grey46", (118, 118, 118)),
    ("Grey50", (128, 128, 128)),
    ("Grey54", (138, 138, 138)),
    ("Grey58", (148, 148, 148)),
    ("Grey62", (158, 158, 158)),
    ("Grey66", (168, 168, 168)),
    ("Grey70", (178, 178, 178)),
    ("Grey74", (188, 188, 188)),
    ("Grey78", (198, 198, 198)),
    ("Grey82", (208, 208, 208)),
    ("Grey85", (218, 218, 218)),
    ("Grey89", (228, 228, 228)),
    ("Grey93", (238, 238, 238)),
])
