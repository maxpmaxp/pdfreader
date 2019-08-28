from ..constants import ESCAPED_CHARS, DEFAULT_ENCODING
from ..types.native import HexString
from ..types.text import TextObject
from .base import BasicTypesParser


class TextParser(BasicTypesParser):
    """ Very poor implementation as we don't support PostScript language in full """

    def __init__(self, fonts, *args, **kwargs):
        self.fonts = fonts
        super(TextParser, self).__init__(*args, **kwargs)
        self.current_font = None
        self.current_strings = []

    @property
    def bf_mapping(self):
        f = self.fonts.get(self.current_font[1:])
        if f:
            return f.ToUnicode.resource.bf_ranges

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
                self.current_font = args[0]
            if self.is_command(token):
                args = []
            else:
                args.append(token)

        res = TextObject(block, self.current_strings)
        self.current_strings = []
        return res

    def decode_char(self, code):
        if code in self.bf_mapping:
            ch = chr(self.bf_mapping.get(code))
            return ch
        raise KeyError(code)

    def hexstring(self):
        s = super(TextParser, self).hexstring()
        # Decode according to the current font settings
        if self.bf_mapping:
            res, raw_res, to_convert = "", "", ""
            for i in range(0, len(s), 2):
                to_convert += s[i:i + 2]
                code = HexString(to_convert).as_int
                try:
                    ch = self.decode_char(code)
                except KeyError:
                    if len(to_convert) <= 2:
                        continue
                    else:
                        # leave as is
                        ch = "\\x{}".format(to_convert)
                raw_res += ch
                res += ESCAPED_CHARS.get(ch, ch)
                to_convert = ""

            res = "({})".format(res)
        else:
            res = raw_res = s
        self.on_string_parsed(raw_res)
        return res

    def skip_until_token(self, name):
        while True:
            if self.current is None:
                break
            self.maybe_spaces()
            if self.current is None:
                break
            obj = self.object()
            if obj == name:
                for _ in range(len(name)):
                    self.prev()
                return True
        return False

    def maybe_spaces(self):
        res = ''
        while self.is_whitespace:
            res += self.next().decode(DEFAULT_ENCODING)
        return res

    def is_command(self, token):
        return token[0] not in '/01234567890+-.<[('