from ansi import *

colors8_dark = {
    "black":    (0, 0, 0),
    "red":      (178, 24, 24),
    "green":    (24, 178, 24),
    "yellow":   (178, 104, 24),
    "blue":     (59, 59, 255),
    "magenta":  (178, 24, 178),
    "cyan":     (24, 178, 178),
    "white":    (178, 178, 178)
}

colors8_bright = {
    "black":    (104, 104, 104),
    "red":      (255, 84, 84),
    "green":    (84, 255, 84),
    "yellow":   (214, 214, 70),
    "blue":     (84, 84, 255),
    "magenta":  (255, 84, 255),
    "cyan":     (84, 255, 255),
    "white":    (255, 255, 255)
}

colors16 = colors8_dark.copy()
colors16.update({"%s_bright" % name: value for name, value in colors8_bright})

colors256 = {} # TODO


class IndexedColor(object):
    def __init__(self, color, palette):
        if type(color) is str:
            self.index = palette.keys.index(color)
        else:
            self.index = color

        self.palette = palette

    @property
    def rgb(self):
        return self.palette.values[self.index]

    @property
    def name(self):
        return self.palette.keys[self.index]

    def __eq__(self, oth):
        return self.rgb == oth.rgb

    def __ne__(self, oth):
        return not (self == oth)


def hex_rgb(rgb):
    return '#%02x%02x%02x' % rgb


class RgbColor(object):
    def __init__(self, r, g, b, name=None):
        self.r = r
        self.g = g
        self.b = b
        self._name = name

    @property
    def rgb(self):
        return (self.r, self.g, self.b)

    @property
    def name(self):
        return self._name if self._name is not None else hex_rgb(self.rgb)

    def __eq__(self, oth):
        return self.rgb == oth.rgb

    def __ne__(self, oth):
        return not (self == oth)


class Document(object):
    def __init__(self, name=""):
        self.name = name
        self.metadata = {}
        self.layers = []

class Layer(object):
    def __init__(self, text="", color=None):
        self.text = text
        self.color = color

class FreeColorLayer(object):
    def __init__(self, width=0, height=0):
        self.matrix = {}
        self.width = width
        self.height = height

    def set_char(self, x, y, char, color=None):
        if y >= self.height:
            self.height = y + 1
        if x >= self.width:
            self.width = self.height + 1

        self.matrix[(x, y)] = (char, color)

    def add_layer(self, layer, offset_x=0, offset_y=0):
        mover = CharMover(offset_x, offset_y)
        for ch in mover.loop(layer.string):
            self.set_char(move.x, mover.y, ch, layer.color)



