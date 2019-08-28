import logging

from ..constants import DEFAULT_ENCODING
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
        val = ""
        if self.current == b'<':
            val += self.dictionary_or_hexstring()
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

    def dictionary(self):
        pfx = self.read(2)
        if pfx != b'<<':
            self.on_parser_error("Dictionary expected")
        res = "<<"
        res += self.maybe_spaces()
        while self.current != b'>':
            res += self.name()
            res += self.maybe_spaces()
            res += self.object()
            res += self.maybe_spaces()
        self.next()
        if self.next() != b'>':
            self.on_parser_error("End of dictionary >> expected ")
        res += ">>"
        return res

    def dictionary_or_hexstring(self):
        if self.current != b"<":
            self.on_parser_error("Dict or hexstring expected")
        self.next()
        val = None
        if self.current == b"<":
            self.prev()
            val = self.dictionary()
        elif self.is_hex_digit:
            self.prev()
            val = self.hexstring()
        else:
            self.on_parser_error("Dict, stream or hexstring expected")
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
        while self.skip_until_token(b'BT'):
            objs.append(self.bt_et())
        return objs

    def bt_et(self):
        block = ""
        args = []
        self.current_strings = []
        token = self.object()
        block += token
        while token != "ET" and not self.is_eof:
            block += self.maybe_spaces()
            if self.is_eof:
                break
            token = self.object()
            block += token
            if token == "Tf":
                self.current_font_name = args[0]
            if self.is_command(token):
                args = []
            else:
                args.append(token)
        if token != "ET":
            logging.warning("BT without closing ET found")
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
        if self.is_eof:
            return False
        window = self.next()
        if self.is_eof:
            return False
        window += self.next()

        while window != name and self.current is not None:
            window = window[1:] + self.next()
        res = window == name
        if res:
            for _ in range(len(name)):
                self.prev()
        return res

    def maybe_spaces(self):
        res = ''
        while self.is_whitespace:
            res += self.next().decode(DEFAULT_ENCODING)
        return res

    def is_command(self, token):
        return token[0] not in '/01234567890+-.<[('