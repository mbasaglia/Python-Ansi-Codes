from xml.sax.saxutils import escape
from .. import tree
from ...ansi import SGR

class SvgFormatter(object):
    flat = False

    def __init__(self, flatten=False, font_size=12):
        self.font_size = font_size
        self.flat = flatten

    @property
    def font_width(self):
        return self.font_size / 2.0

    def document(self, doc):

        if self.flat:
            layers = [self.layer(doc.flattened())]
        else:
            layers = (self.layer(layer) for layer in doc.layers)

        return """<?xml version='1.0' encoding='UTF-8' ?>
            <svg xmlns='http://www.w3.org/2000/svg' width='{width}' height='{height}'>
            <rect style='fill:black;stroke:none;' width='{width}' height='{height}' x='0' y='0' />
            {layers}
        </svg>""".format(
            width=doc.width * self.font_width,
            height=doc.height * self.font_size,
            layers="\n".join(layers)
        )
        return self.layer(doc.flattened())

    def layer(self, layer):
        css = [
            "font-family:monospace",
            "font-size:%spx" % self.font_size,
            "font-weight:bold",
        ]

        if isinstance(layer, tree.Layer):
            css.append("fill:%s" % self.color(layer.color))
            css.append("letter-spacing:-%spx" % (self.font_width * 0.2))
            text = ""
            y = 0
            for line in layer.text.split("\n"):
                y += 1
                text += "<tspan x='{x}' y='{y}'>{line}</tspan>\n".format(
                    x=0,
                    y=y * self.font_size,
                    line=escape(line)
                )
        elif isinstance(layer, tree.FreeColorLayer):
            text = ""
            prev_color = None
            for pos, item in layer.matrix.iteritems():
                char, color = item
                if color is not tree.UnchangedColor and color != prev_color:
                    prev_color = color
                text += "<tspan x='{x}' y='{y}' style='fill:{color};'>{char}</tspan>\n".format(
                    x=pos[0] * self.font_width,
                    y=pos[1] * self.font_size,
                    color=self.color(prev_color),
                    char=escape(char)

                )
        else:
            raise TypeError("Expected layer type")

        return """<text y='0' x='0' style='{style}' xml:space='preserve'>
            {text}
        </text>""".format(
            style=";".join(css),
            text=text
        )

    def color(self, color):
        if color is None:
            return "inherit"
        return tree.hex_rgb(color.rgb)
