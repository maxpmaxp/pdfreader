from ..buffer import Buffer
from ..constants import WHITESPACES, EOL, DELIMITERS, CR, LF, STRING_ESCAPED, DEFAULT_ENCODING
from ..types import *
from ..exceptions import ParserException


class BasicTypesParser(object):
    """ can parse basic PDF types  """

    exception_class = ParserException
    indirect_references_allowed = True
    empty_names_allowed = True

    def __init__(self, fileobj_or_buffer, offset=0):
        if isinstance(fileobj_or_buffer, Buffer):
            self.buffer = fileobj_or_buffer
        else:
            self.buffer = Buffer(fileobj_or_buffer, offset)

    @property
    def current(self):
        return self.buffer.current

    @property
    def is_eof(self):
        return self.buffer.is_eof

    def next(self):
        return self.buffer.next()

    def prev(self):
        return self.buffer.prev()

    def read(self, n):
        return self.buffer.read(n)

    def read_backward(self, n):
        return self.buffer.read_backward(n)

    def get_state(self):
        return self.buffer.get_state()

    def set_state(self, state):
        return self.buffer.set_state(state)

    def reset(self, n):
        return self.buffer.reset(n)

    def on_parser_error(self, message):
        # ToDo: display parsing context here
        raise self.exception_class(message)

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
        res = ''
        while self.current == b'%':
            comments.append(self.comment())
            self.maybe_spaces()
        if comments:
            # return multiline comment
            res = Comment("\n".join(comments))
        return res

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

        >>> s = b'null'
        >>> BasicTypesParser(s, 0).null() is null
        True

        >>> s = b'none'
        >>> BasicTypesParser(s, 0).null()
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

        >>> s = b'true'
        >>> BasicTypesParser(s, 0).true()
        True

        >>> s = b'True'
        >>> BasicTypesParser(s, 0).true()
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


        >>> s = b'false'
        >>> BasicTypesParser(s, 0).false()
        False

        >>> s = b'False'
        >>> BasicTypesParser(s, 0).false()
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

        >>> s = b'%any occurance of %-sign outside of string or stream until EOL (not including) is a comment\\n'
        >>> BasicTypesParser(s, 0).comment()
        '%any occurance of %-sign outside of string or stream until EOL (not including) is a comment'

        Empty comment
        >>> s = b'%\\n'
        >>> BasicTypesParser(s, 0).comment()
        '%'
        """
        if self.current != b"%":
            self.on_parser_error("% expected")
        line = b""
        while not self.is_eol:
            line += self.next()
        self.eol()
        return Comment(line.decode(DEFAULT_ENCODING))

    def numeric(self):
        """

        >>> s = b'0'
        >>> BasicTypesParser(s, 0).numeric()
        0

        >>> s = b'123'
        >>> BasicTypesParser(s, 0).numeric()
        123

        >>> s = b'+123'
        >>> BasicTypesParser(s, 0).numeric()
        123

        >>> s = b'-123'
        >>> BasicTypesParser(s, 0).numeric()
        -123

        >>> s = b'-3.5'
        >>> BasicTypesParser(s, 0).numeric()
        Decimal('-3.5')

        >>> s = b'+3.0'
        >>> BasicTypesParser(s, 0).numeric()
        Decimal('3.0')

        >>> s = b'.01'
        >>> BasicTypesParser(s, 0).numeric()
        Decimal('0.01')

        >>> s = b'+.01'
        >>> BasicTypesParser(s, 0).numeric()
        Decimal('0.01')

        >>> s = b'-.01'
        >>> BasicTypesParser(s, 0).numeric()
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
            val = int(ipart.decode(DEFAULT_ENCODING))
        else:
            val = Decimal("{}.{}".format(ipart.decode(DEFAULT_ENCODING), fpart.decode(DEFAULT_ENCODING)))

        if is_negative:
            val = -val

        return val

    def non_negative_int(self):
        n = self.numeric()
        if not isinstance(n, Integer) or n < 0:
            self.on_parser_error("Non negative int expected")
        return n

    def name(self):
        """
        >>> s = b'/Name'
        >>> BasicTypesParser(s, 0).name()
        'Name'

        >>> s = b'/Name#20with#20spaces'
        >>> BasicTypesParser(s, 0).name()
        'Name with spaces'

        >>> s = b'/Name#with!^speci_#0_als#'
        >>> BasicTypesParser(s, 0).name()
        'Name#with!^speci_#0_als#'

        >>> s = b'/'
        >>> BasicTypesParser(s, 0).name()
        ''

        >>> s = b'/'
        >>> p = BasicTypesParser(s, 0)
        >>> p.empty_names_allowed = False
        >>> p.name()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Empty /Name found

        >>> s = b'Name'
        >>> BasicTypesParser(s, 0).name()
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
                    token += chr(int(code.decode(DEFAULT_ENCODING), 16)).encode(DEFAULT_ENCODING)
                else:
                    # leave as is
                    token += b'#' + code
            else:
                token += self.next()
        if not self.empty_names_allowed and not token:
            self.on_parser_error("Empty /Name found")

        return Name(token.decode(DEFAULT_ENCODING))

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
                val = self._stream(val)
        elif self.is_hex_digit or self.is_whitespace or self.current == b'>':
            # < 09FF> and <> are possible
            self.prev()
            val = self.hexstring()
        else:
            self.on_parser_error("Dict, stream or hexstring expected")
        return val

    def dictionary(self):
        """

        >>> s = b'<<>>'
        >>> BasicTypesParser(s, 0).dictionary()
        {}

        >>> s = b'''<< /Type /Example
        ...            /Subtype /DictExample
        ...            /Version 0.01
        ...            /IntegerItem 12
        ...            /StringItem (a string)
        ...            /ArrayItem [1 2]
        ...            /ObjRef 12 0 R
        ...            /SubDictionary <<
        ...                                 /Item1 true
        ...                                 /Item2 false
        ...                                 /Item3 null
        ...                                 /Item4 (OK)
        ...                           >>
        ...         >>'''
        >>> expected = {'Type': 'Example', 'Subtype': 'DictExample', 'Version': Decimal('0.01'), 'IntegerItem': 12,
        ... 'StringItem': b'a string', 'ArrayItem': [1, 2], 'ObjRef': IndirectReference(12, 0),
        ... 'SubDictionary': {'Item1': True, 'Item2': False, 'Item3': None, 'Item4': b'OK'}}
        >>> BasicTypesParser(s, 0).dictionary() == expected
        True

        """
        pfx = self.read(2)
        if pfx != b'<<':
            self.on_parser_error("Dictionary expected")
        res = {}
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

    def stream(self):
        """
        Parses stream (dict + binary data)

        >>> s = b'''<<
        ... /Length 10
        ... >>
        ... stream\\r\\n***data***\\nendstream'''
        >>> BasicTypesParser(s, 0).stream()
        <Stream:len=10,data=b'***data***'>

        """
        d = self.dictionary()
        # binary data comes after dict
        self.maybe_spaces_or_comments()
        return self._stream(d)

    def _stream(self, d):
        """
        Parses binary data which is part of Stream object itself

        >>> d = dict(Length=10)

        >>> s = b'stream\\r\\n***data***\\nendstream'
        >>> BasicTypesParser(s, 0)._stream(d).stream
        b'***data***'

        >>> s = b'stream\\n***data***\\r\\nendstream'
        >>> BasicTypesParser(s, 0)._stream(d).stream
        b'***data***'

        >>> s = b'stream\\n***data***\\rendstream'
        >>> BasicTypesParser(s, 0)._stream(d).stream
        b'***data***'

        Work around wrong length. See https://github.com/maxpmaxp/pdfreader/issues/68
        1. Length greater than real data length
        >>> d = dict(Length=2)
        >>> s = b'''stream\\n\\nendstream\\n\\n\\n\\n\\n\\n'''
        >>> BasicTypesParser(s, 0)._stream(d).stream
        b''

        2. Length less than real data length
        >>> d = dict(Length=1)
        >>> s = b'''stream\\n***data***\\nendstream\\n\\n\\n\\n\\n'''
        >>> BasicTypesParser(s, 0)._stream(d).stream
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
            logging.debug("Missing LF after `stream` token - [CR]LF expected. Trying to proceed.")
            self.prev()

        state = self.get_state()

        data = self.read(length)
        # According to the spec EOL should be after the data and before endstream
        # But some files do not follow this.
        #
        # See data/leesoil-cases-2.pdf
        #
        # self.eol()
        self.maybe_spaces()
        token = self.read(9)
        if token != b'endstream':
            # Work around wrong length. See https://github.com/maxpmaxp/pdfreader/issues/68
            err_state = self.get_state()
            logging.debug("Wrong stream length: {}. Trying to work around the issue.".format(length))
            self.set_state(state)
            data = self.read(9)
            while not data.endswith(b'endstream'):
                ch = self.next()
                if ch is None:
                    self.set_state(err_state)
                    self.on_parser_error("endstream expected")
                data += ch

            data = data[:-9]
            while data and data[-1:] in EOL:
                data = data[:-1]

        return Stream(d, data)

    def hexstring(self):
        """
        >>> s = b'<01020a0B>'
        >>> BasicTypesParser(s, 0).hexstring()
        '01020A0B'


        >>> s = b'<0>'
        >>> BasicTypesParser(s, 0).hexstring()
        '00'

        >>> s = b'<01 AA FF 1>'
        >>> BasicTypesParser(s, 0).hexstring()
        '01AAFF10'

        >>> s = b'<>'
        >>> BasicTypesParser(s, 0).hexstring()
        ''

        >>> s = b'<0011XX>'
        >>> BasicTypesParser(s, 0).hexstring()
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

        ch = self.next()
        if ch != b'>':
            self.on_parser_error("Wrong hexadecimal string")
        if len(token) % 2:
            # if there is an odd number of digits - the last one should be assumed 0
            token += b'0'
        return HexString(token.decode(DEFAULT_ENCODING).upper())

    def array(self):
        """

        >>> s = b'[]'
        >>> BasicTypesParser(s, 0).array()
        []

        >>> s = b'[-1.5 <AABBCC> (Regular string) <</Name /Value>> 0 10 5 R]'
        >>> BasicTypesParser(s, 0).array()
        [Decimal('-1.5'), 'AABBCC', b'Regular string', {'Name': 'Value'}, 0, <IndirectReference:n=10,g=5>]

        """
        if self.current != b'[':
            self.on_parser_error("Array expected")
        self.next()
        array = Array()
        self.maybe_spaces_or_comments()
        while self.current != b']':
            array.append(self.object())
            self.maybe_spaces_or_comments()
        self.next()  # skip enclosing bracket
        return array

    def string(self):
        """
        The following are valid literal strings

        >>> s = b'(This is a string)'
        >>> BasicTypesParser(s, 0).string()
        b'This is a string'

        >>> s = b'''(Strings may contain newlines
        ... and such.)'''
        >>> BasicTypesParser(s, 0).string()
        b'Strings may contain newlines\\nand such.'

        >>> s = b'''(Strings may contain balanced parenthesis () and special characters (*!&}^% and so on).)'''
        >>> BasicTypesParser(s, 0).string()
        b'Strings may contain balanced parenthesis () and special characters (*!&}^% and so on).'

        Empty strings are allowed
        >>> s = b'()'
        >>> BasicTypesParser(s, 0).string()
        b''

        Multiline strings come with reverse solidus wollowed by CR, LF or the both.
        >>> s = b'''(This is \\
        ... a multiline \\
        ... string)'''
        >>> BasicTypesParser(s, 0).string()
        b'This is a multiline string'

        >>> s = b'(This string has escaped chars in it \\\\n\\\\r\\\\t\\\\b\\\\f\\\\(\\\\)\\\\\\\\)'
        >>> BasicTypesParser(s, 0).string()
        b'This string has escaped chars in it \\n\\r\\t\\x08\\x0c()\\\\'

        >>> s = b'(This string contains 2 \\\\245octal characters\\\\307)'
        >>> BasicTypesParser(s, 0).string()
        b'This string contains 2 ¥octal charactersÇ'

        >>> s = b'(The octal ddd may contain 1,2 or 3 octal digits: \\\\2,\\\\20,\\\\245)'
        >>> BasicTypesParser(s, 0).string()
        b'The octal ddd may contain 1,2 or 3 octal digits: \\x02,\\x10,¥'

        >>> s = b'(\\\\0053 denotes 2 characters Ctl+E followed by the digit 3)'
        >>> BasicTypesParser(s, 0).string()
        b'\\x053 denotes 2 characters Ctl+E followed by the digit 3'
        """

        if self.current != b'(':
            self.on_parser_error("String expected")
        val = b''
        self.next()
        while True:
            ch = self.next()
            if ch == b'(':
                self.prev()
                val += b"(" + self.string() + b")"
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
                        val += bytes([icode])
                    else:
                        # leave as is
                        val += b"\\" + code
                elif ch in EOL:
                    # multiline string - just skip
                    self.prev()
                    self.eol()
                else:
                    # unescape or leave as is
                    val += STRING_ESCAPED.get(ch) or (b"\\" + ch)
            elif ch == b')':
                break
            else:
                val += ch
        return String(val)

    def _get_parser(self):
        method = None
        if self.current == b'<':
            method = self.dictionary_or_stream_or_hexstring
        elif self.current == b'[':
            method = self.array
        elif self.current == b'(':
            method = self.string
        elif self.current == b'n':
            method = self.null
        elif self.current == b'f':
            method = self.false
        elif self.current == b't':
            method = self.true
        elif self.current in b'+-.':
            method = self.numeric
        elif self.current in b'1234567890':
            if self.indirect_references_allowed:
                method = self.numeric_or_indirect_reference
            else:
                method = self.numeric
        elif self.current == b"/":
            method = self.name
        return method

    def object(self):
        val = None
        self.maybe_spaces_or_comments()
        method = self._get_parser()
        if method:
            val = method()
        else:
            self.on_parser_error("Unexpected token")
        return val

    def indirect_reference(self):
        """
        >>> s = b'10 5 R'
        >>> BasicTypesParser(s, 0).indirect_reference()
        <IndirectReference:n=10,g=5>

        """
        num = self.non_negative_int()
        self.maybe_spaces_or_comments()
        gen = self.non_negative_int()
        self.maybe_spaces_or_comments()
        ch = self.next()
        if ch != b'R':
            self.on_parser_error('R keyword expected')
        return IndirectReference(num, gen)

    def numeric_or_indirect_reference(self):
        state = self.get_state()
        try:
            val = self.indirect_reference()
        except ParserException:
            self.set_state(state)
            val = self.numeric()
        return val

    def token(self):
        """ just a token which does not belong to any of PDF types like: def, findresource, ET, BT
            >>> s = b'def'
            >>> BasicTypesParser(s, 0).token()
            'def'

            >>> s = b'T*'
            >>> BasicTypesParser(s, 0).token()
            'T*'

            >>> s = b'10T*'
            >>> BasicTypesParser(s, 0).token()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.ParserException: Regular non-digit character expected
        """
        if not self.is_regular or self.is_digit:
            self.on_parser_error("Regular non-digit character expected")

        token = b''
        while self.is_regular:
            token += self.next()
        return Token(token.decode(DEFAULT_ENCODING))

    def expected_name(self, value):
        name = self.name()
        if name != value:
            self.on_parser_error("%s expected".format(value))
        return name

    def expected_token(self, value):
        token = self.token()
        if token != value:
            self.on_parser_error("%s expected".format(value))
        return token

    def expected_numeric(self, value):
        n = self.numeric()
        if n != value:
            self.on_parser_error("%s expected".format(value))
        return n


if __name__ == "__main__":
    import doctest
    doctest.testmod()
