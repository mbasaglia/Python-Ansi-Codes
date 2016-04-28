from .. import tree

class TextFormatter(object):
    flat = True

    def document(self, doc, output):
        self.layer(doc.flattened(), output)

    def layer(self, layer, output):
        if isinstance(layer, tree.Layer):
            output.write(layer.text)
        elif isinstance(layer, tree.FreeColorLayer):
            prev_color = None
            for y in xrange(layer.height):
                for x in xrange(layer.width):
                    char, color = layer.matrix.get((x, y), (" ", None))
                    output.write(char)
                output.write("\n")
        else:
            raise TypeError("Expected layer type")

    def color(self, color):
        return ""
