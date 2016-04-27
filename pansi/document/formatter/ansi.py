from io import StringIO
from .. import tree
from ...ansi import SGR

class AnsiFormatter(object):
    flat = True

    def document(self, doc):
        return self.layer(doc.flattened())

    def layer(self, layer):
        if isinstance(layer, tree.Layer):
            return self.color(layer.color) + layer.text

        if isinstance(layer, tree.FreeColorLayer):
            text = ""
            prev_color = None
            for y in xrange(layer.height):
                for x in xrange(layer.width):
                    char, color = layer.matrix.get((x, y), (" ", tree.UnchangedColor))
                    if color is not tree.UnchangedColor and color != prev_color:
                        prev_color = color
                        text += self.color(color)
                    text += char
                text += "\n"
            return text

        raise TypeError("Expected layer type")

    def color(self, color):
        if color is None:
            ansi_color = SGR.ResetColor
        elif isinstance(color, tree.RgbColor):
            ansi_color = SGR.ColorRGB(color.r, color.g, color.b)
        elif isinstance(color, tree.IndexedColor):
            if len(color.palette) == 8:
                bright = getattr(color.palette, "bright", False)
                ansi_color = SGR.Color(color.index, False, bright)
            elif len(color.palette) == 16:
                ansi_color = SGR.Color(color.index & 7, False, color.index > 7)
            else:
                ansi_color = SGR.Color256(color.index)
        elif type(color) is tuple and len(color) == 3:
            ansi_color = SGR.ColorRGB(*color)
        else:
            raise TypeError("Expected document color")

        return repr(SGR(ansi_color))
