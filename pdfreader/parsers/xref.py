from ..constants import EOL, SP, NULL, TAB
from ..exceptions import TokenNotFound, ParserException
from ..xref import XRef
from .base import PDFParser


class RegularXrefParser(PDFParser):
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
        >>> from io import BytesIO
        >>> b = BytesIO(s)
        >>> p = RegularXrefParser(b, 0)
        >>> p.parse()
        <XRef:free=1,in_use=20>

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
        while self.current in (NULL, TAB, SP):
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
