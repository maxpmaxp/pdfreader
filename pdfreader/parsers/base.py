from ..buffer import Buffer
from ..constants import WHITESPACE_CODES, WHITESPACES, EOL, DELIMITERS, CR, LF, STRING_ESCAPED
from ..exceptions import ParserException
from ..types import *


class BaseParser(Buffer):

    def parse(self):
        raise NotImplementedError()

    def on_parser_error(self, message):
        raise ParserException(message)

    @staticmethod
    def is_empty_line(bline):
        """
        Checks if a bytes line is empty regarding PDF syntax

        >>> from pdfreader.constants import WHITESPACES
        >>> BaseParser.is_empty_line(b''.join(WHITESPACES))
        True

        >>> BaseParser.is_empty_line(b''.join(WHITESPACES) + b''.join(WHITESPACES))
        True

        >>> BaseParser.is_empty_line(b'')
        True

        >>> BaseParser.is_empty_line(b'%PDF-1.6\\n\\n')
        False

        >>> BaseParser.is_empty_line(b'%%EOF')
        False
        """
        return bline == b'' or all(c in WHITESPACE_CODES for c in bline)

    def spaces(self):
        if self.is_whitespace:
            self.on_parser_error("Whitespace character expected")
        self.maybe_spaces()

    def maybe_spaces(self):
        while self.is_whitespace:
            self.next()

    def maybe_spaces_or_comments(self):
        self.maybe_spaces()
        comments = []
        while self.current == b'%':
            comments.append(self.comment())
            self.maybe_spaces()
        if comments:
            # return multiline comment
            return Comment("\n".join(comments))

    def eol(self):
        """ EOL is either CR or LF or the both """
        if self.current not in EOL:
            self.on_parser_error("EOL expected")
        self.maybe_eol()

    def maybe_eol(self):
        """ EOL is either CR or LF or the both except for the streams """
        if self.current == CR:
            self.next()
            if self.current == LF:
                self.next()
        elif self.current == LF:
            self.next()

    @property
    def is_eol(self):
        return self.current is not None and self.current in EOL

    @property
    def is_whitespace(self):
        return self.current is not None and self.current in WHITESPACES

    @property
    def is_delimiter(self):
        return self.current is not None and self.current in DELIMITERS

    @property
    def is_regular(self):
        return self.current is not None and not (self.is_whitespace or self.is_delimiter)

    @property
    def is_digit(self):
        return self.current is not None and self.current in b'0123456789'

    @property
    def is_hex_digit(self):
        return self.current is not None and self.current in b'0123456789ABCDEFabcdef'

    def null(self):
        """
        null token

        >>> from io import BytesIO
        >>> s = BytesIO(b'null')
        >>> BaseParser(s, 0).null() is null
        True

        >>> s = BytesIO(b'none')
        >>> BaseParser(s, 0).null()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: null token expected
        """
        val = self.read(4)
        if val != b'null':
            self.on_parser_error("null token expected")
        return null

    def true(self):
        """
        true token

        >>> from io import BytesIO
        >>> s = BytesIO(b'true')
        >>> BaseParser(s, 0).true()
        True

        >>> s = BytesIO(b'True')
        >>> BaseParser(s, 0).true()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: true token expected
        """
        val = self.read(4)
        if val != b'true':
            self.on_parser_error("true token expected")
        return True

    def false(self):
        """
        false token

        >>> from io import BytesIO
        >>> s = BytesIO(b'false')
        >>> BaseParser(s, 0).false()
        False

        >>> s = BytesIO(b'False')
        >>> BaseParser(s, 0).false()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: false token expected
        """
        val = self.read(5)
        if val != b'false':
            self.on_parser_error("false token expected")
        return False

    def comment(self):
        """
        >>> from io import BytesIO
        >>> s = BytesIO(b'%any occurance of %-sign outside of string or stream until EOL (not including) is a comment\\n')
        >>> BaseParser(s, 0).comment()
        '%any occurance of %-sign outside of string or stream until EOL (not including) is a comment'

        Empty comment
        >>> s = BytesIO(b'%\\n')
        >>> BaseParser(s, 0).comment()
        '%'
        """
        if self.current != b"%":
            self.on_parser_error("% expected")
        line = b""
        while not self.is_eol:
            line += self.next()
        self.eol()
        return Comment(line.decode("ascii"))

    def numeric(self):
        """
        >>> from io import BytesIO
        >>> s = BytesIO(b'0')
        >>> BaseParser(s, 0).numeric()
        0

        >>> s = BytesIO(b'123')
        >>> BaseParser(s, 0).numeric()
        123

        >>> s = BytesIO(b'+123')
        >>> BaseParser(s, 0).numeric()
        123

        >>> s = BytesIO(b'-123')
        >>> BaseParser(s, 0).numeric()
        -123

        >>> s = BytesIO(b'-3.5')
        >>> BaseParser(s, 0).numeric()
        Decimal('-3.5')

        >>> s = BytesIO(b'+3.0')
        >>> BaseParser(s, 0).numeric()
        Decimal('3.0')

        >>> s = BytesIO(b'.01')
        >>> BaseParser(s, 0).numeric()
        Decimal('0.01')

        >>> s = BytesIO(b'+.01')
        >>> BaseParser(s, 0).numeric()
        Decimal('0.01')

        >>> s = BytesIO(b'-.01')
        >>> BaseParser(s, 0).numeric()
        Decimal('-0.01')

        """
        is_negative = False
        is_integer = True
        if self.current == b"+":
            self.next()
        elif self.current == b"-":
            is_negative = True
            self.next()
        ipart, fpart = b'', b''

        # read integer part
        while self.is_digit:
            ipart += self.current
            self.next()

        # read point if exists
        if self.current == b'.':
            is_integer = False
            self.next()
            while self.is_digit:
                fpart += self.next()

        if not ipart and not fpart:
            self.on_parser_error("Invalid numeric token")

        if not ipart:
            ipart = b'0'
        if not fpart:
            fpart = b'0'

        if is_integer:
            val = int(ipart.decode("ascii"))
        else:
            val = Decimal("{}.{}".format(ipart.decode("ascii"), fpart.decode("ascii")))

        if is_negative:
            val = -val

        return val

    def name(self):
        """
        >>> from io import BytesIO
        >>> s = BytesIO(b'/Name')
        >>> BaseParser(s, 0).name()
        'Name'

        >>> from io import BytesIO
        >>> s = BytesIO(b'/Name#20with#20spaces')
        >>> BaseParser(s, 0).name()
        'Name with spaces'

        >>> from io import BytesIO
        >>> s = BytesIO(b'/Name#with!^speci_#0_als#')
        >>> BaseParser(s, 0).name()
        'Name#with!^speci_#0_als#'

        >>> from io import BytesIO
        >>> s = BytesIO(b'/')
        >>> BaseParser(s, 0).name()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Empty /Name found

        >>> from io import BytesIO
        >>> s = BytesIO(b'Name')
        >>> BaseParser(s, 0).name()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Name token expected


        """
        if self.current != b'/':
            self.on_parser_error("Name token expected")
        token = b''
        self.next()
        while self.is_regular:
            if self.current == b'#':
                self.next()
                code = b''
                for i in range(2):
                    if not self.is_hex_digit:
                        break
                    code += self.next()
                if len(code) == 2:
                    # must be exactly 2 characters
                    token += chr(int(code.decode("ascii"), 16)).encode('ascii')
                else:
                    # leave as is
                    token += b'#' + code
            else:
                token += self.next()
        if not token:
            self.on_parser_error("Empty /Name found")

        return Name(token.decode("ascii"))

    def dictionary_or_stream_or_hexstring(self):
        if self.current != b"<":
            self.on_parser_error("Dict or hexstring expected")
        self.next()
        val = None
        if self.current == b"<":
            self.prev()
            val = self.dictionary()
            # stream may come after the dict
            self.maybe_spaces_or_comments()
            if self.current == b's':
                val = self.stream(val)
        elif self.is_hex_digit:
            self.prev()
            val = self.hexstring()
        else:
            self.on_parser_error("Dict, stream or hexstring expected")
        return val

    def dictionary(self):
        """
        >>> from io import BytesIO
        >>> s = BytesIO(b'<<>>')
        >>> BaseParser(s, 0).dictionary()
        {}

        >>> from io import BytesIO
        >>> s = b'''<< /Type /Example
        ...            /Subtype /DictExample
        ...            /Version 0.01
        ...            /IntegerItem 12
        ...            /StringItem (a string)
        ...            /ArrayItem [1 2]
        ...            /SubDictionary <<
        ...                                 /Item1 true
        ...                                 /Item2 false
        ...                                 /Item3 null
        ...                                 /Item4 (OK)
        ...                           >>
        ...         >>'''
        >>> BaseParser(BytesIO(s), 0).dictionary()
        {'Type': 'Example', 'Subtype': 'DictExample', 'Version': Decimal('0.01'), 'IntegerItem': 12, 'StringItem': 'a string', 'ArrayItem': [1, 2], 'SubDictionary': {'Item1': True, 'Item2': False, 'Item3': None, 'Item4': 'OK'}}

        """
        pfx = self.read(2)
        if pfx != b'<<':
            self.on_parser_error("Dictionary expected")
        res = dict()
        self.maybe_spaces_or_comments()
        while self.current != b'>':
            key = self.name()
            self.maybe_spaces_or_comments()
            res[key] = self.object()
            self.maybe_spaces_or_comments()
        self.next()
        if self.next() != b'>':
            self.on_parser_error("End of dictionary >> expected ")
        return res

    def stream(self, d):
        """
        >>> from io import BytesIO
        >>> d = dict(Length=10)

        >>> s = BytesIO(b'stream\\r\\n***data***\\nendstream')
        >>> BaseParser(s, 0).stream(d).stream
        b'***data***'

        >>> s = BytesIO(b'stream\\n***data***\\r\\nendstream')
        >>> BaseParser(s, 0).stream(d).stream
        b'***data***'

        >>> s = BytesIO(b'stream\\n***data***\\rendstream')
        >>> BaseParser(s, 0).stream(d).stream
        b'***data***'

        """
        length = d['Length']
        token = self.read(6)
        if token != b'stream':
            self.on_parser_error("stream expected")
        # `stream` keyword must be followed by CR+LF or by LF, but NOT by CR alone
        ch = self.next()
        if ch == CR:
            ch = self.next()
        if ch != LF:
            self.on_parser_error("Wrong stream newline: [CR]LF expected")
        data = self.read(length)
        self.eol()

        token = self.read(9)
        if token != b'endstream':
            self.on_parser_error("endstream expected")
        return Stream(d, data)

    def hexstring(self):
        """
        >>> from io import BytesIO
        >>> s = BytesIO(b'<01020a0B>')
        >>> BaseParser(s, 0).hexstring()
        '01020A0B'

        >>> from io import BytesIO
        >>> s = BytesIO(b'<0>')
        >>> BaseParser(s, 0).hexstring()
        '00'

        >>> from io import BytesIO
        >>> s = BytesIO(b'<01 AA FF 1>')
        >>> BaseParser(s, 0).hexstring()
        '01AAFF10'

        >>> from io import BytesIO
        >>> s = BytesIO(b'<>')
        >>> BaseParser(s, 0).hexstring()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Wrong hexadecimal string


        >>> from io import BytesIO
        >>> s = BytesIO(b'<0011XX>')
        >>> BaseParser(s, 0).hexstring()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Wrong hexadecimal string

        """
        if self.current != b"<":
            self.on_parser_error("Hexadecimal string expected")
        self.next()
        token = b''
        self.maybe_spaces_or_comments()
        while self.is_hex_digit:
            token += self.next()
            self.maybe_spaces_or_comments()
        if not token:
            self.on_parser_error("Wrong hexadecimal string")
        ch = self.next()
        if ch != b'>':
            self.on_parser_error("Wrong hexadecimal string")
        if len(token) % 2:
            # if there is an odd number of digits - the last one should be assumed 0
            token += b'0'
        return HexString(token.decode('ascii').upper())

    def array(self):
        """
        >>> from io import BytesIO
        >>> s = BytesIO(b'[]')
        >>> BaseParser(s, 0).array()
        []

        >>> from io import BytesIO
        >>> s = BytesIO(b'[-1.5 <AABBCC> (Regular string) <</Name /Value>>]')
        >>> BaseParser(s, 0).array()
        [Decimal('-1.5'), 'AABBCC', 'Regular string', {'Name': 'Value'}]

        """
        if self.current != b'[':
            self.on_parser_error("Array expected")
        self.next()
        array = Array()
        self.maybe_spaces_or_comments()
        while self.current != b']':
            array.append(self.object())
            self.maybe_spaces_or_comments()
        self.next() # skip enclosing bracket
        return array

    def string(self):
        """
        >>> from io import BytesIO

        The following are valid literal strings

        >>> s = b'(This is a string)'
        >>> BaseParser(BytesIO(s), 0).string()
        'This is a string'

        >>> s = b'''(Strings may contain newlines
        ... and such.)'''
        >>> BaseParser(BytesIO(s), 0).string()
        'Strings may contain newlines\\nand such.'

        >>> s = b'''(Strings may contain balanced parenthesis () and special characters (*!&}^% and so on).)'''
        >>> BaseParser(BytesIO(s), 0).string()
        'Strings may contain balanced parenthesis () and special characters (*!&}^% and so on).'

        Empty strings are allowed
        >>> s = b'()'
        >>> BaseParser(BytesIO(s), 0).string()
        ''

        Multiline strings come with reverse solidus wollowed by CR, LF or the both.
        >>> s = b'''(This is \\
        ... a multiline \\
        ... string)'''
        >>> BaseParser(BytesIO(s), 0).string()
        'This is a multiline string'

        >>> s = b'(This string has escaped chars in it \\\\n\\\\r\\\\t\\\\b\\\\f\\\\(\\\\)\\\\\\\\)'
        >>> BaseParser(BytesIO(s), 0).string()
        'This string has escaped chars in it \\n\\r\\t\\x08\\x0c()\\\\'

        >>> s = b'(This string contains 2 \\\\245octal characters\\\\307)'
        >>> BaseParser(BytesIO(s), 0).string()
        'This string contains 2 ¥octal charactersÇ'

        >>> s = b'(The octal ddd may contain 1,2 or 3 octal digits: \\\\2,\\\\20,\\\\245)'
        >>> BaseParser(BytesIO(s), 0).string()
        'The octal ddd may contain 1,2 or 3 octal digits: \\x02,\\x10,¥'

        >>> s = b'(\\\\0053 denotes 2 characters Ctl+E followed by the digit 3)'
        >>> BaseParser(BytesIO(s), 0).string()
        '\\x053 denotes 2 characters Ctl+E followed by the digit 3'
        """

        if self.current != b'(':
            self.on_parser_error("String expected")
        val = ''
        self.next()
        while True:
            ch = self.next()
            if ch == b'(':
                self.prev()
                val += "(" + self.string() + ")"
            elif ch == b'\\':
                ch = self.next()
                if ch in b"01234567":
                    # octal code comes up to 3 characters
                    code = ch
                    for _ in range(2):
                        if self.current not in b"01234567":
                            break
                        code += self.next()
                    icode = int(code, 8)
                    # 8 bits values are allowed only
                    if icode <= 255:
                        val += chr(icode)
                    else:
                        # leave as is
                        val += "\\" + code.decode("ascii")
                elif ch in EOL:
                    # multiline string - just skip
                    self.eol()
                else:
                    # unescape or leave as is
                    val += STRING_ESCAPED.get(ch) or (b"\\" + ch).decode('ascii')
            elif ch == b')':
                break
            else:
                val += ch.decode("ascii")
        return String(val)

    def object(self):
        val = None
        self.maybe_spaces_or_comments()
        if self.current == b'<':
            val = self.dictionary_or_stream_or_hexstring()
        elif self.current == b'[':
            val = self.array()
        elif self.current == b'(':
            val = self.string()
        elif self.current == b'n':
            val = self.null()
        elif self.current == b'f':
            val = self.false()
        elif self.current == b't':
            val = self.true()
        elif self.current in b'+-.1234567890':
            val = self.numeric()
        elif self.current == b"/":
            val = self.name()
        else:
            import pdb; pdb.set_trace()
            self.on_parser_error("Unexpected token")
        self.maybe_spaces_or_comments()
        return val

    def indirect_object(self):
        """
        >>> s = b'''12 0 obj
        ...     (Brilling)
        ... endobj'''
        >>> BaseParser(s, 0).indirect_object()
        <IndirectObject:n=12,g=0,v='Brilling'>
        """
        num = self.numeric()
        if not isinstance(num, Integer):
            self.on_parser_error("Wrong object number")

        self.maybe_spaces_or_comments()
        gen = self.numeric()
        if not isinstance(gen, Integer):
            self.on_parser_error("Wrong object generation")

        self.maybe_spaces_or_comments()
        token = self.read(3)
        if token != b"obj":
            self.on_parser_error("obj expected")

        self.maybe_spaces_or_comments()
        val = self.object()
        self.maybe_spaces_or_comments()

        token = self.read(6)
        if token != b"endobj":
            self.on_parser_error("endobj expected")

        return IndirectObject(num, gen, val)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
