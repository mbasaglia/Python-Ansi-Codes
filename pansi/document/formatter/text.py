from .. import tree

class TextFormatter(object):
    flat = True

    def document(self, doc):
        return self.layer(doc.flattened())

    def layer(self, layer):
        if isinstance(layer, tree.Layer):
            return layer.text
        if isinstance(layer, tree.FreeColorLayer):
            text = ""
            prev_color = None
            for y in xrange(layer.height):
                for x in xrange(layer.width):
                    char, color = layer.matrix.get((x, y), (" ", None))
                    text += char
                text += "\n"
            return text
        raise TypeError("Expected layer type")

    def color(self, color):
        return ""
