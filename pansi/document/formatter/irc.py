from .. import tree

# TODO Color conversions
class IrcFormatter(object):
    flat = True
    colors = [
        "01", "05", "03", "07", "02", "06", "10", "15",
        "14", "04", "09", "08", "12", "13", "11", "00"
    ]

    def document(self, doc, output):
        self.layer(doc.flattened(), output)

    def layer(self, layer, output):
        if isinstance(layer, tree.Layer):
            output.write(self.color(layer.color) + layer.text)
        elif isinstance(layer, tree.FreeColorLayer):
            prev_color = None
            for y in xrange(layer.height):
                output.write("\x0301,01")
                for x in xrange(layer.width):
                    char, color = layer.matrix.get((x, y), (" ", tree.UnchangedColor))
                    if color is not tree.UnchangedColor and color != prev_color:
                        prev_color = color
                        output.write(self.color(color))
                    output.write(char)
                output.write("\n")
        else:
            raise TypeError("Expected layer type")

    def color(self, color):
        if color is None:
            return "\x0f"
        elif isinstance(color, tree.IndexedColor):
            if len(color.palette) == 8:
                bright = 8 if getattr(color.palette, "bright", False) else 0
                code = self.colors[color.index + bright]
            elif len(color.palette) == 16:
                code = self.colors[color.index]
        else:
            raise TypeError("Expected document color")

        return "\x03%s,01" % code
