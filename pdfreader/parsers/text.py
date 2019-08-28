from ..constants import ESCAPED_CHARS, DEFAULT_ENCODING
from ..types.native import HexString
from ..types.text import TextObject
from .base import BasicTypesParser


class TextParser(BasicTypesParser):
    """ Very poor implementation as we don't support PostScript language in full """

    def __init__(self, fonts, *args, **kwargs):
        self.fonts = fonts
        super(TextParser, self).__init__(*args, **kwargs)
        self.current_font_name = None
        self.current_strings = []

    @property
    def current_font(self):
        if self.current_font_name:
            return self.fonts[self.current_font_name[1:]]

    def on_string_parsed(self, s):
        self.current_strings.append(s)

    def object(self):
        val = self.maybe_spaces()
        if self.current == b'<':
            val += self.hexstring()
        elif self.current == b'[':
            val += self.array()
        elif self.current == b'(':
            val += self.string()
        elif self.current in b'+-.1234567890':
            val += str(self.numeric())
        elif self.current == b"/":
            val += self.name()
        elif self.is_regular:
            val += self.token()
        else:
            self.on_parser_error("Unexpected token")
        return val

    def array(self):
        val = ""
        if self.current != b'[':
            self.on_parser_error("Array expected")
        self.next()
        val += "["
        val += self.maybe_spaces()
        while self.current != b']':
            val += self.object()
            val += self.maybe_spaces()
        self.next()  # skip enclosing bracket
        val += "]"
        return val

    def name(self):
        s = super(TextParser, self).name()
        return "/" + s

    def text(self):
        """
        Returns a list of TextObjects parsed from stream
        """
        objs = []
        while self.skip_until_token("BT"):
            objs.append(self.bt_et())
        return objs

    def bt_et(self):
        block = ""
        args = []
        self.current_strings = []
        token = self.object()
        block += token
        while token != "ET":
            block += self.maybe_spaces()
            token = self.object()
            block += token
            if token == "Tf":
                self.current_font_name = args[0]
            if self.is_command(token):
                args = []
            else:
                args.append(token)

        res = TextObject(block, self.current_strings)
        self.current_strings = []
        return res

    def hexstring(self):
        s = super(TextParser, self).hexstring()
        if self.current_font:
            s = self.current_font.decode_hexstring(s)
        self.on_string_parsed(s)
        return "({})".format(s)

    def string(self):
        s = super(TextParser, self).string()
        if self.current_font:
            s = self.current_font.decode_string(s)
        self.on_string_parsed(s)
        return "({})".format(s)

    def skip_until_token(self, name):
        self.maybe_spaces()
        window = self.read(len(name))
        while window != name and self.current is not None:
            window = window[1:] + self.next()
        return window == name

    def maybe_spaces(self):
        res = ''
        while self.is_whitespace:
            res += self.next().decode(DEFAULT_ENCODING)
        return res

    def is_command(self, token):
        return token[0] not in '/01234567890+-.<[('