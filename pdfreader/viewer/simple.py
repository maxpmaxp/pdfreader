import logging

from ..codecs.decoder import Decoder, default_decoder
from ..parsers.content import ContentParser
from ..types.native import HexString, String
from ..types.objects import Image, Form
from ..utils import pdf_escape_string
from .base import Viewer
from .canvas import SimpleCanvas


def object_to_string(obj):
    return ""


class SimpleViewer(Viewer):

    parser_class = ContentParser
    canvas_class = SimpleCanvas
    operators_to_handlers = {"'": "apostrophe",
                             '"': "quotation",
                             'T*': "Tstar"}

    def __init__(self, doc):
        super(SimpleViewer, self).__init__(doc)
        self.bracket_commands_stack = [] # one day we may start support BX/EX, MDC/BMC/EMC.
                                         # BI/EI comes as a part of ContentParser due to inline image object nature
        self._decoders = dict()

    @property
    def mode(self):
        """ Current interpreter mode reflects the most recent command brackets """
        if self.bracket_commands_stack:
            return self.bracket_commands_stack[-1].name

    @property
    def decoder(self):
        name = self.gss.state.font_name
        if name not in self._decoders:
            if name in self.resources.Font:
                obj = Decoder(self.resources.Font[name])
            else:
                obj = default_decoder
            self._decoders[name] = obj
        return self._decoders[name]

    def decode_string(self, s):
        if isinstance(s, HexString):
            s = self.decoder.decode_hexstring(s)
        else:
            s = self.decoder.decode_string(s)
        return s

    def after_handler(self, obj):
        """ Put object on canvas """
        self.canvas.text += object_to_string(obj)

    def on_inline_image(self, obj):
        self.canvas.inline_images.append(obj)

    def on_Do(self, op):
        name = op.args[0]
        xobj = self.resources.XObject.get(name)
        if not xobj:
            logging.warning("Can't locate XObject {}".format(name))
        else:
            if isinstance(xobj, Image):
                self.canvas.images.append(xobj)
            elif isinstance(xobj, Form):
                self.canvas.forms.append(xobj)

    def on_BT(self, op):
        if self.mode == "BT":
            raise ValueError("BT operator without enclosing ET")
        self.bracket_commands_stack.append(op)

    def on_ET(self, op):
        if self.mode != "BT":
            raise ValueError("ET operator without corresponding BT")
        self.bracket_commands_stack.pop()

    # Text handlers
    def on_Tf(self, op):
        """ Set font name and size """
        self.gss.state.Font = op.args

    def on_Tj(self, op):
        """ Show text string
            Decode it, add on canvas.strings and replace operator's argument
        """
        s = self.decode_string(op.args[0])
        self.canvas.strings.append(s)
        op.args = ["({})".format(pdf_escape_string(s))]

    on_apostrophe = on_Tj

    def on_TJ(self, op):
        """ Show one or more text strings  """
        for i in len(op.args):
            if isinstance(op.args[i], (HexString, String)):
                s = self.decode_string(op.args[i])
                self.canvas.strings.append(s)
                op.args[i] = "({})".format(pdf_escape_string(s))

    on_quotation = on_TJ

    def on_Tstar(self, op):
        """ Moves start to the next line.
            Does it make sence to add "\n" to canvas.strings ???
            Do nothing until figure out
        """
        pass