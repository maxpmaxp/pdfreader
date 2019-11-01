import logging

from ..constants import DEFAULT_ENCODING
from ..exceptions import ParserException
from ..types.content import TextObject
from ..types.native import HexString
from .base import BasicTypesParser


class BaseDecoder(object):
    def __init__(self, font):
        self.cmap = font.get("ToUnicode")
        self.encoding = font.get('Encoding')

    def decode_string(self, s):
        s_hex = HexString("".join(hex(b)[2:].zfill(2) for b in s.encode(DEFAULT_ENCODING)))
        return self.decode_hexstring(s_hex)

    def decode_hexstring(self, s: HexString):
        raise NotImplementedError()


class CMAPDecoder(BaseDecoder):

    def decode_hexstring(self, s: HexString):
        res, code = "", ""

        for i in range(0, len(s), 2):
            code += s[i:i + 2]
            try:
                ch = self.cmap.bf_ranges[code]
            except KeyError:
                if len(code) < 4:
                    continue
                elif self.encoding:
                    # According to the spec we may ignore encoding if CMAP defined but prefer to not.
                    ch = HexString(code).to_bytes().decode(self.encoding)
                else:
                    # leave as is
                    ch = HexString(code).to_string()
            res += ch
            code = ""

        if code:
            hs = HexString(code)
            res += hs.to_bytes().decode(self.encoding) if self.encoding else hs.to_string()

        return res


class EncodingDecoder(BaseDecoder):

    def decode_hexstring(self, s: HexString, encoding=None):
        # ToDo: Differences support. See p263 PDF32000_2008.pdf
        encoding = self.encoding

        # replace expert encodings with regular & warn
        if encoding == "MacExpertEncoding":
            logging.warning("Replacing MacExpertEncoding with MacRomanEncoding")
            encoding = "MacRomanEncoding"

        if encoding == "WinAnsiEncoding":
            py_encoding = 'cp1252'
        elif encoding == "MacRomanEncoding":
            # ToDO: Not 100% correct there are some differences between MacRomanEncoding and macroman
            py_encoding = 'macroman'
        elif encoding == "StandardEncoding":
            # ToDO: Not 100% correct
            py_encoding = 'latin1'
        elif encoding in ("Identity-H", "Identity-V"):
            # It maps 2 byte character to the same 2 byte character
            py_encoding = 'latin1'
        else:
            logging.warning("Unsupported encoding {}. Using default {}".format(encoding, DEFAULT_ENCODING))
            py_encoding = DEFAULT_ENCODING

        if cmap:
            res = cmap.resource.decode_hexstring(s, encoding=py_encoding)
        elif encoding:
            val = s.to_bytes()
            try:
                res = val.decode(py_encoding)
            except UnicodeDecodeError:
                logging.warning("Incorrect bytes: {}".format(repr(val)))
                res = val.decode(py_encoding, "replace")
        else:
            res = s.to_string()
        return res

    def decode_string(self, s):
        s_hex = HexString("".join(hex(b)[2:].zfill(2) for b in s.encode(DEFAULT_ENCODING)))
        return self.decode_hexstring(s_hex)


def Decoder(font):
    klass = CMAPDecoder if font.get("ToUnicode") else EncodingDecoder
    return klass(font)


class TextParser(BasicTypesParser):
    """ BT/ET section parser """

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

    def text(self):
        """
        Returns a list of TextObjects parsed from stream
        """
        objs = []
        for o in self.parse_objects():
            if isinstance(o, TextObject):
                objs.append(o)
        return objs

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

    def maybe_spaces(self):
        res = ''
        while self.is_whitespace:
            res += self.next().decode(DEFAULT_ENCODING)
        return res

    def is_command(self, token):
        return token[0] not in '/01234567890+-.<[('