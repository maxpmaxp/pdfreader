from ..constants import EOL, SP, SPACES
from ..exceptions import EOFException, TokenNotFound, ParserException
from ..filestructure import Trailer
from ..xref import XRef
from .base import BaseParser


class TrailerParser(BaseParser):
    """
    Acrobat viewers require only that the header appear somewhere within the last 1024 bytes of the file
    """
    EOF = b"%%EOF"

    def __init__(self, fileobj):
        super(TrailerParser, self).__init__(fileobj, -1024)

    def parse(self):
        """ Parsers fileobj trailer and returns Trailer object
        """
        xref_offset = self.find_xref_offset()
        try:
            xref = self.parse_regular_xref(xref_offset)
        except TokenNotFound:
            xref = self.parse_indirect_xref(xref_offset)
        return Trailer(xref)

    def parse_regular_xref(self, offset):
        parser = RegularXrefParser(self.fileobj, offset)
        return parser.parse()

    def parse_indirect_xref(self, offset):
        self.reset(offset)
        # xref may come as indirect object
        raise NotImplementedError()

    def gen_lines_forward(self):
        state = 'start'
        line = b""
        while True:
            try:
                ch = self.next()
            except EOFException:
                break
            if state == "start":
                if ch in EOL:
                    continue
                else:
                    state = 'in-line'
                    line += ch
            elif state == 'in-line':
                if ch in EOL:
                    yield line
                    line = b""
                    state = 'start'
                else:
                    line = ch + line
        yield line

    def gen_lines_backward(self):
        state = 'start'
        line = b""
        while True:
            try:
                ch = self.prev()
            except EOFException:
                break
            if state == "start":
                if ch in EOL:
                    continue
                else:
                    state = 'in-line'
                    line = ch + line
            elif state == 'in-line':
                if ch in EOL:
                    yield line
                    line = b""
                    state = 'start'
                else:
                    line = ch + line
        yield line

    def find_xref_offset(self):
        """ locate xref offset

            >>> from io import BytesIO
            >>> f = BytesIO(b'%PDF-1.6\\nxref\\nblablabla\\nstartxref\\n9\\n%%EOF')
            >>> p = TrailerParser(f)
            >>> p.find_xref_offset()
            9

            >>> from io import BytesIO
            >>> f = BytesIO(b'%PDF-1.6\\nxref\\nblablabla\\nstartxref\\r%comment\\n9\\n%comment\\n%%EOF')
            >>> p = TrailerParser(f)
            >>> p.find_xref_offset()
            9

            >>> from io import BytesIO
            >>> f = BytesIO(b'%PDF-1.6\\nxref\\nblablabla\\nstartxref\\r%comment\\nXXX\\n%comment\\n%%EOF')
            >>> p = TrailerParser(f)
            >>> p.find_xref_offset()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.TokenNotFound: wrong startxref size


            >>> from io import BytesIO
            >>> f = BytesIO(b'%PDF-1.6\\nxref\\nblablabla\\r%comment\\n9\\n%comment\\n%%EOF')
            >>> p = TrailerParser(f)
            >>> p.find_xref_offset()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.TokenNotFound: startxref


        """
        self.locate_eof()
        xref_offset = None
        for line in self.gen_lines_backward():
            line = line.strip()
            if line.startswith(b"%") or self.is_empty_line(line):
                continue
            if xref_offset is None:
                try:
                    xref_offset = int(line)
                except ValueError:
                    raise TokenNotFound('wrong startxref size')
            else:
                if line == b'startxref':
                    break
                raise TokenNotFound('startxref')
        return xref_offset

    def locate_eof(self):
        """ sets buffer pointer to the last byte before EOF

            >>> from io import BytesIO
            >>> f = BytesIO(b'%PDF-1.6\\nblablabla\\n%%EOF')
            >>> TrailerParser(f).locate_eof()
            True

            >>> from io import BytesIO
            >>> f = BytesIO(b'%PDF-1.6\\nblablabla\\n%%EOF ')
            >>> TrailerParser(f).locate_eof()
            True

            >>> f = BytesIO(b'%IPS-Adobe-1.3 PDF-1.6\\nblablabla\\n%%EOF\\r\\n%comment')
            >>> TrailerParser(f).locate_eof()
            True

            Test missing header and one out of 1024 leading bytes

            >>> f = BytesIO(b'\\n%PDF-1.5\\nblablabla\\n%%EOF\\n'  +b' '*1020)
            >>> TrailerParser(f).locate_eof()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.TokenNotFound: b'%%EOF'


            >>> f = BytesIO(b'\\nblablabla'*100)
            >>> TrailerParser(f).locate_eof()
            Traceback (most recent call last):
            ...
            pdfreader.exceptions.TokenNotFound: b'%%EOF'
        """
        for line in self.gen_lines_backward():
            if len(self.data) > self.block_size:
                break
            if line.startswith(self.EOF):
                return True
        raise TokenNotFound(self.EOF)

    def locate_token(self, data, token):
        """ Returns offset of the token starting from the end of data.
            Raises TokenNotFound if not found
        """
        assert isinstance(data, bytes)
        assert isinstance(token, bytes)


class RegularXrefParser(BaseParser):
    """ Parses xref represented directly
    """

    def parse(self):
        self.xref()
        self.maybe_spaces()
        self.maybe_comment()
        self.eol()
        xref = XRef()
        while self.current in b'0123456789':
            first_object, n_entries = self.range()
            self.eol()
            for i in range(n_entries):
                offset, gen, flag = self.entry()
                xref.add_entry(offset, first_object + i, gen, flag)
        return xref

    def xref(self):
        token = b"".join([self.next() for _ in range(4)])
        if token != b'xref':
            raise TokenNotFound("xref")

    def eol(self):
        ch = self.current
        if ch not in EOL:
            raise ParserException("EOL expected")
        while self.current in EOL:
            self.next()

    def maybe_spaces(self):
        while self.current in SPACES:
            self.next()

    def maybe_comment(self):
        if self.current == b"%":
            while self.current not in EOL:
                self.next()

    def range(self):
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

    def entry(self):
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


if __name__ == "__main__":
    import doctest
    doctest.testmod()
