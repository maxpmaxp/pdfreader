import logging

from ..codecs.decoder import default_decoder
from ..constants import DEFAULT_ENCODING
from ..exceptions import ParserException
from ..types.content import TextObject
from .base import BasicTypesParser


class TextParser(BasicTypesParser):
    """ BT/ET section parser """

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super(TextParser, self).__init__(*args, **kwargs)
        self.current_font_name = None
        self.current_strings = []

    @property
    def decoder(self):
        if self.current_font_name:
            decoder = self.context.decoders[self.current_font_name[1:]]
        else:
            decoder = default_decoder
        return decoder

    def on_string_parsed(self, s):
        self.current_strings.append(s)

    def object(self):
        if self.current is None:
            raise ParserException("Character expected")
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

    def text_object(self):
        block = ""
        args = []
        self.current_strings = []
        try:
            token = self.object()
            block += token
            while token != "ET" and not self.is_eof:
                block += self.maybe_spaces()
                token = self.object()
                block += token
                if token == "BT":
                    self.prev()
                    self.prev()
                    raise ParserException("BT without enclosing ET")
                if token == "Tf":
                    self.current_font_name = args[0]
                if self.is_command(token):
                    args = []
                else:
                    args.append(token)
        except ParserException:
            logging.warning("Inconsistent BT ET block detected:\n{}".format(block))

        res = TextObject(block, self.current_strings)
        self.current_strings = []
        return res

    def hexstring(self):
        s = super(TextParser, self).hexstring()
        if self.decoder:
            s = self.decoder.decode_hexstring(s)
        self.on_string_parsed(s)
        return "({})".format(s)

    def string(self):
        s = super(TextParser, self).string()
        if self.decoder:
            s = self.decoder.decode_string(s)
        self.on_string_parsed(s)
        return "({})".format(s)

    def maybe_spaces(self):
        res = ''
        while self.is_whitespace:
            res += self.next().decode(DEFAULT_ENCODING)
        return res

    def is_command(self, token):
        return token[0] not in '/01234567890+-.<[('