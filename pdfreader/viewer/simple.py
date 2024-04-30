import logging
log = logging.getLogger(__name__)
from base64 import b85encode

from pdfreader.constants import DEFAULT_ENCODING

from ..codecs.decoder import Decoder, default_decoder
from ..filters import asciihex, ascii85
from ..parsers.content import ContentParser
from ..types.content import Operator, InlineImage
from ..types.native import HexString, String, Dictionary, Array, Boolean, Name, Decimal, Integer
from ..types.objects import Image, Form
from ..utils import pdf_escape_string
from .canvas import SimpleCanvas
from .resources import Resources
from .pdfviewer import PDFViewer, ContextualViewer

ascii_filters = asciihex.filter_names + ascii85.filter_names

def object_to_string(obj):
    if obj is None:
        val = "null"
    elif isinstance(obj, Boolean):
        val = str(obj).lower()
    elif isinstance(obj, Name):
        val = "/" + obj
    elif isinstance(obj, str):
        val = obj
    elif isinstance(obj, (int, Integer, Decimal)):
        val = str(obj)
    elif isinstance(obj, Array):
        val = "[" + " ".join([object_to_string(elm) for elm in obj]) + "]"
    elif isinstance(obj, Dictionary):
        val = "<<" + " ".join(["/{} {}".format(k, object_to_string(v)) for k, v in obj.items()]) + ">>"
    elif isinstance(obj, Operator):
        operands = " ".join([object_to_string(a) for a in obj.args])
        val = "\n{} {}".format(operands, obj.name)
    elif isinstance(obj, InlineImage):
        # Convert bytes to string representation
        # We encode the image with ASCII85 to make it a unicode string
        entries = " ".join(["/{} {}".format(k, object_to_string(v))
                            for k, v in obj.dictionary.items()
                            if k not in ('F', 'Filter')])
        new_filters = obj.Filter if isinstance(obj.Filter, list) else [obj.Filter]
        last_filter = new_filters[0]
        if last_filter in ascii_filters:
            # data stream contains ASCII characters
            content = obj.data
        else:
            # encode binary content with ASCII85Decode to make in human-readable
            new_filters = ["ASCII85Decode"] + new_filters
            content = b85encode(obj.data) + b'~>'

        str_filters = "".join([" /{} ".format(f) for f in new_filters])
        entries += " /Filter [{}]".format(str_filters)
        val = "\nBI\n{entries}\nID\n{content}\nEI".format(entries=entries, content=content.decode('ascii'))
    elif isinstance(obj, bytes):
        log.debug("Binary data. Using default encoding. Possibly arg of unsupported operator: {}".format(repr(bytes)))
        val = obj.decode(DEFAULT_ENCODING, 'replace')
    else:
        raise ValueError("Unexpected object: {}. Possibly a bug.".format(obj))
    return val


class TextOperatorsMixin(object):

    parser_class = ContentParser
    canvas_class = SimpleCanvas
    operators_aliases = {"'": "apostrophe",
                         '"': "quotation",
                         'T*': "Tstar"}

    def __init__(self, *args, **kwargs):
        super(TextOperatorsMixin, self).__init__(*args, **kwargs)
        self.bracket_commands_stack = [] # one day we may start support BX/EX, MDC/BMC/EMC.
                                         # BI/EI comes as a part of ContentParser due to inline image object nature
        self._decoders = {}

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
        self.canvas.text_content += object_to_string(obj)

    def on_inline_image(self, obj):
        self.canvas.inline_images.append(obj)

    def on_BT(self, op):
        if self.mode == "BT":
            log.debug("BT operator without enclosing ET. Trying to recover.")
            self.bracket_commands_stack.pop()
        self.bracket_commands_stack.append(op)

    def on_ET(self, op):
        if self.mode != "BT":
            log.debug("ET operator without corresponding BT. Trying to recover.")
        else:
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
        arr = op.args[0]
        for i in range(len(arr)):
            if isinstance(arr[i], (HexString, String)):
                s = self.decode_string(arr[i])
                self.canvas.strings.append(s)
                arr[i] = "({})".format(pdf_escape_string(s))

    on_quotation = on_TJ

    def on_Tstar(self, op):
        """ Moves start to the next line.
            Does it make sence to add "\n" to canvas.strings ???
            Do nothing until figure out
        """
        pass

    def _decode_prop_contents(self, op):
        """ Decode content on properties list.
            But doesn't add on canvas strings.
        """
        tag, props = op.args
        if isinstance(props, dict):
            contents = props.get('Contents')
            if isinstance(contents, bytes):
                props['Contents'] = self.decode_string(contents)

    on_DP = _decode_prop_contents
    on_BDC = _decode_prop_contents


class SimplePDFViewer(TextOperatorsMixin, PDFViewer):
    """ Simple PDF document interpreter (viewer).
          - uses :class:`~pdfreader.document.PDFDocument` as document navigation engine
          - renders document page content onto :class:`~pdfreader.viewer.SimpleCanvas`
          - has graphical state

        On initialization automatically navigates to the 1st page.

        :param fobj: file-like object: binary file descriptor, BytesIO stream etc.
        :param password: Optional. Password to access PDF content.

    """

    #: Current page canvas - :class:`~pdfreader.viewer.SimpleCanvas` instance
    canvas = None

    #: Reflects current graphical state. :class:`~pdfreader.viewer.GraphicsStateStack` instance.
    gss = None

    #: Current page resources. :class:`~pdfreader.viewer.Resources` instance.
    resources = None

    #: Contains current page number
    current_page_number = None

    def __init__(self, *args, **kwargs):
        self._canvas_cache = {} # canvas cache
        super(SimplePDFViewer, self).__init__(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return

    def render(self):
        if self.current_page_number not in self._canvas_cache:
            super(SimplePDFViewer, self).render()
            self._canvas_cache[self.current_page_number] = self.canvas.copy()
        else:
            self.canvas = self._canvas_cache[self.current_page_number].copy()

    def after_navigate(self, n):
        self._decoders = {}
        self.bracket_commands_stack = []
        super(SimplePDFViewer, self).after_navigate(n)

    def on_Do(self, op):
        name = op.args[0]
        xobj = self.resources.XObject.get(name)
        if not xobj:
            log.debug("Can't locate XObject {}".format(name))
        else:
            if isinstance(xobj, Image) and name not in self.canvas.forms:
                self.canvas.images[name] = xobj
            elif isinstance(xobj, Form) and name not in self.canvas.forms:
                # render form and save
                rs = [xobj.Resources] if xobj.Resources else []
                resources = Resources.from_page(self.current_page, resources_stack=rs)
                subviewer = FormViewer(xobj.filtered, resources, self.gss)
                subviewer.render()
                self.canvas.forms[name] = subviewer.canvas


class FormViewer(TextOperatorsMixin, ContextualViewer):
    """ Forms sub-viewer  """
    pass
