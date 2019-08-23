import re

from .buffer import Buffer
from .constants import WHITESPACE_CODES, WHITESPACES, EOL, DELIMITERS, CR, LF, SP, STRING_ESCAPED, DEFAULT_ENCODING
from .exceptions import ParserException
from .types import *
from .filestructure import Header, Trailer
from .xref import XRef, XRefEntry


class PDFParser(Buffer):
    PDF_HEADER = re.compile(b"^%PDF-(\d\.\d)", re.MULTILINE)
    IPS_HEADER = re.compile(b"^%IPS-Adobe-\d\.\d PDF-(\d\.\d)", re.MULTILINE)

    def __init__(self, fileobj, offset=0):
        super(PDFParser, self).__init__(fileobj, offset)


    def on_parser_error(self, message):
        # ToDo: display parsing context here
        raise ParserException(message)

    @staticmethod
    def is_empty_line(bline):
        """
        Checks if a bytes line is empty regarding PDF syntax

        >>> from pdfreader.constants import WHITESPACES
        >>> PDFParser.is_empty_line(b''.join(WHITESPACES))
        True

        >>> PDFParser.is_empty_line(b''.join(WHITESPACES) + b''.join(WHITESPACES))
        True

        >>> PDFParser.is_empty_line(b'')
        True

        >>> PDFParser.is_empty_line(b'%PDF-1.6\\n\\n')
        False

        >>> PDFParser.is_empty_line(b'%%EOF')
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

        >>> s = b'null'
        >>> PDFParser(s, 0).null() is null
        True

        >>> s = b'none'
        >>> PDFParser(s, 0).null()
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
        >>> PDFParser(s, 0).true()
        True

        >>> s = b'True'
        >>> PDFParser(s, 0).true()
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
        >>> PDFParser(s, 0).false()
        False

        >>> s = b'False'
        >>> PDFParser(s, 0).false()
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
        >>> PDFParser(s, 0).comment()
        '%any occurance of %-sign outside of string or stream until EOL (not including) is a comment'

        Empty comment
        >>> s = b'%\\n'
        >>> PDFParser(s, 0).comment()
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
        >>> PDFParser(s, 0).numeric()
        0

        >>> s = b'123'
        >>> PDFParser(s, 0).numeric()
        123

        >>> s = b'+123'
        >>> PDFParser(s, 0).numeric()
        123

        >>> s = b'-123'
        >>> PDFParser(s, 0).numeric()
        -123

        >>> s = b'-3.5'
        >>> PDFParser(s, 0).numeric()
        Decimal('-3.5')

        >>> s = b'+3.0'
        >>> PDFParser(s, 0).numeric()
        Decimal('3.0')

        >>> s = b'.01'
        >>> PDFParser(s, 0).numeric()
        Decimal('0.01')

        >>> s = b'+.01'
        >>> PDFParser(s, 0).numeric()
        Decimal('0.01')

        >>> s = b'-.01'
        >>> PDFParser(s, 0).numeric()
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
        >>> PDFParser(s, 0).name()
        'Name'

        >>> s = b'/Name#20with#20spaces'
        >>> PDFParser(s, 0).name()
        'Name with spaces'

        >>> s = b'/Name#with!^speci_#0_als#'
        >>> PDFParser(s, 0).name()
        'Name#with!^speci_#0_als#'

        >>> s = b'/'
        >>> PDFParser(s, 0).name()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Empty /Name found

        >>> s = b'Name'
        >>> PDFParser(s, 0).name()
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
        if not token:
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
        elif self.is_hex_digit:
            self.prev()
            val = self.hexstring()
        else:
            self.on_parser_error("Dict, stream or hexstring expected")
        return val

    def dictionary(self):
        """

        >>> s = b'<<>>'
        >>> PDFParser(s, 0).dictionary()
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
        >>> PDFParser(s, 0).dictionary()
        {'Type': 'Example', 'Subtype': 'DictExample', 'Version': Decimal('0.01'), 'IntegerItem': 12, 'StringItem': 'a string', 'ArrayItem': [1, 2], 'ObjRef': <IndirectReference:n=12,g=0>, 'SubDictionary': {'Item1': True, 'Item2': False, 'Item3': None, 'Item4': 'OK'}}

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

    def stream(self):
        """
        Parses stream (dict + binary data)

        >>> s = b'''<<
        ... /Length 10
        ... >>
        ... stream\\r\\n***data***\\nendstream'''
        >>> PDFParser(s, 0).stream()
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
        >>> PDFParser(s, 0)._stream(d).stream
        b'***data***'

        >>> s = b'stream\\n***data***\\r\\nendstream'
        >>> PDFParser(s, 0)._stream(d).stream
        b'***data***'

        >>> s = b'stream\\n***data***\\rendstream'
        >>> PDFParser(s, 0)._stream(d).stream
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
        >>> s = b'<01020a0B>'
        >>> PDFParser(s, 0).hexstring()
        '01020A0B'


        >>> s = b'<0>'
        >>> PDFParser(s, 0).hexstring()
        '00'


        >>> s = b'<01 AA FF 1>'
        >>> PDFParser(s, 0).hexstring()
        '01AAFF10'

        >>> s = b'<>'
        >>> PDFParser(s, 0).hexstring()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: Wrong hexadecimal string

        >>> s = b'<0011XX>'
        >>> PDFParser(s, 0).hexstring()
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
        return HexString(token.decode(DEFAULT_ENCODING).upper())

    def array(self):
        """

        >>> s = b'[]'
        >>> PDFParser(s, 0).array()
        []

        >>> s = b'[-1.5 <AABBCC> (Regular string) <</Name /Value>> 0 10 5 R]'
        >>> PDFParser(s, 0).array()
        [Decimal('-1.5'), 'AABBCC', 'Regular string', {'Name': 'Value'}, 0, <IndirectReference:n=10,g=5>]

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
        >>> PDFParser(s, 0).string()
        'This is a string'

        >>> s = b'''(Strings may contain newlines
        ... and such.)'''
        >>> PDFParser(s, 0).string()
        'Strings may contain newlines\\nand such.'

        >>> s = b'''(Strings may contain balanced parenthesis () and special characters (*!&}^% and so on).)'''
        >>> PDFParser(s, 0).string()
        'Strings may contain balanced parenthesis () and special characters (*!&}^% and so on).'

        Empty strings are allowed
        >>> s = b'()'
        >>> PDFParser(s, 0).string()
        ''

        Multiline strings come with reverse solidus wollowed by CR, LF or the both.
        >>> s = b'''(This is \\
        ... a multiline \\
        ... string)'''
        >>> PDFParser(s, 0).string()
        'This is a multiline string'

        >>> s = b'(This string has escaped chars in it \\\\n\\\\r\\\\t\\\\b\\\\f\\\\(\\\\)\\\\\\\\)'
        >>> PDFParser(s, 0).string()
        'This string has escaped chars in it \\n\\r\\t\\x08\\x0c()\\\\'

        >>> s = b'(This string contains 2 \\\\245octal characters\\\\307)'
        >>> PDFParser(s, 0).string()
        'This string contains 2 ¥octal charactersÇ'

        >>> s = b'(The octal ddd may contain 1,2 or 3 octal digits: \\\\2,\\\\20,\\\\245)'
        >>> PDFParser(s, 0).string()
        'The octal ddd may contain 1,2 or 3 octal digits: \\x02,\\x10,¥'

        >>> s = b'(\\\\0053 denotes 2 characters Ctl+E followed by the digit 3)'
        >>> PDFParser(s, 0).string()
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
                        val += "\\" + code.decode(DEFAULT_ENCODING)
                elif ch in EOL:
                    # multiline string - just skip
                    self.eol()
                else:
                    # unescape or leave as is
                    val += STRING_ESCAPED.get(ch) or (b"\\" + ch).decode(DEFAULT_ENCODING)
            elif ch == b')':
                break
            else:
                val += ch.decode(DEFAULT_ENCODING)
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
        elif self.current in b'+-.':
            val = self.numeric()
        elif self.current in b'1234567890':
            val = self.numeric_or_indirect_reference()
        elif self.current == b"/":
            val = self.name()
        else:
            self.on_parser_error("Unexpected token")
        self.maybe_spaces_or_comments()
        return val

    def numeric_or_indirect_reference(self):
        self.push_state()
        try:
            val = self.indirect_reference()
        except ParserException:
            self.pop_state()
            val = self.numeric()
        return val

    def indirect_object(self):
        """
        >>> s = b'''12 0 obj
        ...     (Brilling)
        ... endobj'''
        >>> PDFParser(s, 0).indirect_object()
        <IndirectObject:n=12,g=0,v='Brilling'>

        """
        begin_offset = self.current_stream_offset
        num = self.non_negative_int()
        self.maybe_spaces_or_comments()
        gen = self.non_negative_int()

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

        obj = IndirectObject(num, gen, val)
        end_offset = self.current_stream_offset
        # handle all known indirect objects
        self.on_parsed_indirect_object(obj, begin_offset, end_offset)
        return obj

    def on_parsed_indirect_object(self, obj, b_offset=None, e_offset=None):
        pass

    def indirect_reference(self):
        """
        >>> s = b'10 5 R'
        >>> PDFParser(s, 0).indirect_reference()
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

    def pdf_header(self):
        """
        1. Acrobat viewers require only that the header appear somewhere within the first 1024 bytes of the file
        2. Acrobat viewers will also accept a header in the form of
        %IPS-Adobe-N.n PDF-M.m

        >>> f = b'%PDF-1.6\\nblablablanblablabla'
        >>> PDFParser(f).pdf_header()
        <PDF Header:v=1.6 (major=1, minor=6), offset=0)>

        >>> f = b'%IPS-Adobe-1.3 PDF-1.6\\nblablabla'
        >>> PDFParser(f).pdf_header()
        <PDF Header:v=1.6 (major=1, minor=6), offset=0)>

        >>> f = b'%some custom heading\\n%PDF-1.5\\nblablabla'
        >>> PDFParser(f).pdf_header()
        <PDF Header:v=1.5 (major=1, minor=5), offset=21)>

        >>> f = b'%some custom heading\\n%IPS-Adobe-1.3 PDF-1.6\\nblablabla'
        >>> PDFParser(f).pdf_header()
        <PDF Header:v=1.6 (major=1, minor=6), offset=21)>

        Test missing header and one out of 1024 leading bytes

        >>> f = b' '*1020 + b'\\n%PDF-1.5\\nblablabla'
        >>> PDFParser(f).pdf_header()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: No PDF header found


        >>> f = b'\\nblablabla'*100
        >>> PDFParser(f).pdf_header()
        Traceback (most recent call last):
        ...
        pdfreader.exceptions.ParserException: No PDF header found

        """
        self.reset(0)
        size = len("%IPS-Adobe-1.3 PDF-1.6") # max header size

        window = self.read(size)
        n_read = size
        m = self.PDF_HEADER.search(window) or self.IPS_HEADER.search(window)
        while m is None and n_read < 1024 and not self.is_eof:
            window = window[1:] + self.next()
            n_read += 1
            m = self.PDF_HEADER.search(window) or self.IPS_HEADER.search(window)
        else:
            if m is None:
                self.on_parser_error("No PDF header found")

        # return current to the beginning of the header
        for _ in range(size):
            self.prev()

        return Header(m.groups()[0].decode(DEFAULT_ENCODING), offset=self.index + m.start())

    def pdf_trailer(self):
        """

        #>>> fd = open('data/tyler-or-DocumentFragment.pdf','rb')
        #>>> fd = open('data/fw8ben.pdf','rb')
        #>>> fd = open('data/leesoil-cases-2.pdf','rb')
        #>>> p = PDFParser(fd).pdf_trailer()

        """
        xref_offset = self.xref_offset()
        self.reset(xref_offset)
        if self.current == b'x':
            # parse direct xref
            xref = self.direct_xref()
            # parse trailer
            # ToDO: parse several xref sections like we do for streams
            self.maybe_spaces_or_comments()
            tdict = self.trailer()
            trailer = Trailer([xref], **tdict)
        else:
            # Assume xref as a stream which may contain liks to the previous xref streams
            last_offset = xref_offset
            all_xrefs = []
            stream_log = []
            tdict = dict()
            while last_offset is not None:
                self.reset(last_offset)
                obj = self.indirect_object()
                if not isinstance(obj.val, Stream) or obj.val["Type"] != "XRef":
                    self.on_parser_error("xref stream expected")
                if not tdict:
                    for k in ('Size', 'Prev', 'Root', 'Encrypt', 'Info', 'ID'):
                        tdict[k] = obj.val.get(k)
                xr = XRef.from_stream(obj.val)
                all_xrefs.append(xr)
                stream_log.append(obj.val)
                last_offset = obj.val.get("Prev")
            trailer = Trailer(all_xrefs, **tdict)
        return trailer

    def trailer(self):
        """ Parses trailer represented directly

            >>> s = b'''trailer
            ... << /Size 22
            ... /Root 2 0 R
            ... /Info 1 0 R
            ... /ID [<0102AA> <0102BB>]
            ... >>'''
            >>> p = PDFParser(s, 0)
            >>> p.trailer()
            {'Size': 22, 'Root': <IndirectReference:n=2,g=0>, 'Info': <IndirectReference:n=1,g=0>, 'ID': ['0102AA', '0102BB']}
        """
        token = self.read(7)
        if token != b'trailer':
            self.on_parser_error("trailer expected")
        self.maybe_spaces_or_comments()
        return self.dictionary()

    def direct_xref(self):
        """ Parses xref represented directly

            >>> s = b'''xref
            ... 0 21
            ... 0000000000 65535 f\\r
            ... 0000000016 00000 n\\r
            ... 0000000241 00000 n\\r
            ... 0000004036 00000 n\\r
            ... 0000590979 00000 n\\r
            ... 0000588331 00000 n\\r
            ... 0000004144 00000 n\\r
            ... 0000004300 00000 n\\r
            ... 0000004456 00000 n\\r
            ... 0000004611 00000 n\\r
            ... 0000004767 00000 n\\r
            ... 0000461285 00000 n\\r
            ... 0000461386 00000 n\\r
            ... 0000331344 00000 n\\r
            ... 0000331445 00000 n\\r
            ... 0000205526 00000 n\\r
            ... 0000205627 00000 n\\r
            ... 0000092926 00000 n\\r
            ... 0000093027 00000 n\\r
            ... 0000004924 00000 n\\r
            ... 0000005025 00000 n\\r
            ... trailer ...'''
            >>> PDFParser(s, 0).direct_xref()
            <XRef:free=1,in_use=20,compressed=0>

        """
        token = self.read(4)
        if token != b'xref':
            self.on_parser_error("xref expected")
        self.maybe_spaces_or_comments()
        xref = XRef()
        while self.current in b'0123456789':
            first_object, n_entries = self.xref_range()
            self.eol()
            for i in range(n_entries):
                offset, gen, flag = self.xref_entry()
                xref.add_entry(XRefEntry(number=first_object + i, offset=offset, generation=gen, typ=flag))
        return xref

    def xref_range(self):
        # read first object number
        d1 = b''
        while self.current != SP:
            d1 += self.next()

        # skip space
        self.next()

        # read number of entities
        d2 = b''
        while self.current not in EOL:
            d2 += self.next()

        try:
            d1, d2 = int(d1), int(d2)
        except ValueError:
            raise ParserException("Wrong xref range")

        return d1, d2

    def xref_entry(self):
        data = b"".join([self.next() for _ in range(20)]).strip()
        offset, gen, flag = data.split(b" ", 2)
        try:
            offset, gen = int(offset), int(gen)
            flag = flag.decode("utf-8")
            if flag not in ('n', 'f'):
                raise ValueError()
        except ValueError:
            raise ParserException("Wrong xref entry: {}".format(data))
        return offset, gen, flag

    def seek_eof(self):
        """ sets buffer pointer to the last byte before EOF

            >>> f = b'%PDF-1.6\\nblablabla\\n%%EOF'
            >>> PDFParser(f).seek_eof()
            True

            >>> f = b'%PDF-1.6\\nblablabla\\n%%EOF '
            >>> PDFParser(f).seek_eof()
            True

            >>> f = b'%IPS-Adobe-1.3 PDF-1.6\\nblablabla\\n%%EOF\\r\\n%comment'
            >>> PDFParser(f).seek_eof()
            True

            Test missing header and one out of 1024 leading bytes

            >>> f = b'\\n%PDF-1.5\\nblablabla\\n%%EOF\\n'  +b' '*1020
            >>> PDFParser(f).seek_eof()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.ParserException: %%EOF not found


            >>> f = b'\\nblablabla'*100
            >>> PDFParser(f).seek_eof()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.ParserException: %%EOF not found
        """
        self.reset(-1024)
        window = b''
        for _ in range(5):
            window = self.prev() + window

        n_read = len(window)

        while n_read < 1024 and not self.is_eof:
            if window == b"%%EOF":
                break
            window = self.prev() + window[:-1]
            n_read += 1
        else:
            self.on_parser_error("%%EOF not found")
        return True

    def xref_offset(self):
        """ locate xref offset

            >>> f = b'%PDF-1.6\\nxref\\nblablabla\\nstartxref\\n9\\n%%EOF'
            >>> p = PDFParser(f)
            >>> p.xref_offset()
            9

            >>> from io import BytesIO
            >>> f = b'%PDF-1.6\\nxref\\nblablabla\\nstartxref\\r%comment\\n9\\n%comment\\n%%EOF'
            >>> p = PDFParser(f)
            >>> p.xref_offset()
            9

            >>> from io import BytesIO
            >>> f = b'%PDF-1.6\\nxref\\nblablabla\\r%comment\\n9\\n%comment\\n%%EOF'
            >>> p = PDFParser(f)
            >>> p.xref_offset()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.ParserException: startxref not found

        """
        self.seek_eof()
        token = b'startxref'
        window = b''
        for _ in range(len(token)):
            window = self.prev() + window

        n_read = len(window)

        while not self.is_eof:
            if window == token:
                break
            window = self.prev() + window[:-1]
            n_read += 1
        else:
            self.on_parser_error("startxref not found")

        self.read(len(token) + 1)
        self.maybe_spaces_or_comments()
        offset = self.non_negative_int()
        return offset


if __name__ == "__main__":
    import doctest

    doctest.testmod()
