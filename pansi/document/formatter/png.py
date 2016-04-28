import cairosvg
from .. import tree
from .svg import SvgFormatter
from StringIO import StringIO

class PngFormatter(object):
    flat = True

    def __init__(self, *args, **kwargs):
        self._svg_formatter = SvgFormatter(*args, **kwargs)

    def document(self, doc, output):
        buffer = StringIO()
        self._svg_formatter.document(doc, buffer)
        cairosvg.svg2png(bytestring=buffer.getvalue(), write_to=output)

    def layer(self, layer, output):
        doc = tree.Document
        doc.layers.append(layer)
        self.document(doc, output)

    def color(self, color):
        return ""
