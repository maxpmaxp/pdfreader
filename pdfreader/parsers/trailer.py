from ..buffer import Buffer
from ..constants import EOL, SP
from ..exceptions import EOFException, TokenNotFound, ParserException
from ..filestructure import Trailer
from ..xref import XRef
from .base import PDFParser


class TrailerParser(Buffer):
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



    def locate_token(self, data, token):
        """ Returns offset of the token starting from the end of data.
            Raises TokenNotFound if not found
        """
        assert isinstance(data, bytes)
        assert isinstance(token, bytes)


class RegularXrefParser(PDFParser):
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



if __name__ == "__main__":
    import doctest
    doctest.testmod()
