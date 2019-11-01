import re

from ..constants import WHITESPACE_CODES, EOL, SP
from ..exceptions import ParserException
from ..types import *

from .base import BasicTypesParser


class PDFParser(BasicTypesParser):
    PDF_HEADER = re.compile(b"^%PDF-(\d\.\d)", re.MULTILINE)
    IPS_HEADER = re.compile(b"^%IPS-Adobe-\d\.\d PDF-(\d\.\d)", re.MULTILINE)

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

    def indirect_object(self):
        """
        >>> s = b'''12 0 obj
        ...     (Brilling)
        ... endobj'''
        >>> PDFParser(s, 0).indirect_object()
        <IndirectObject:n=12,g=0,v=b'Brilling'>

        """
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
        return obj

    def startxref(self):
        """ Can be in the doc body if any incremental updates done

            >>> s = b'''startxref
            ...     0'''
            >>> PDFParser(s, 0).startxref()
            <StartXRef: 0>
        """
        token = self.read(9)
        if token != b'startxref':
            self.on_parser_error('startxref expected')
        self.maybe_spaces_or_comments()
        offset = self.non_negative_int()
        return StartXRef(offset)

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

        return PDFHeader(m.groups()[0].decode(DEFAULT_ENCODING), offset=self.buffer.index + m.start())

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
            all_xrefs = [self.direct_xref()]
            # parse trailer
            self.maybe_spaces_or_comments()
            t = last_trailer = self.trailer()
            prev_xref_offset = t.params.get("Prev")
            while prev_xref_offset:
                self.reset(prev_xref_offset)
                all_xrefs.append(self.direct_xref())
                # parse previous trailer
                self.maybe_spaces_or_comments()
                t = self.trailer()
                prev_xref_offset = t.params.get("Prev")

            trailer = PDFTrailer(all_xrefs, **last_trailer.params)
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
            trailer = PDFTrailer(all_xrefs, **tdict)
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
            <Trailer: {'Size': 22, 'Root': <IndirectReference:n=2,g=0>, 'Info': <IndirectReference:n=1,g=0>, 'ID': ['0102AA', '0102BB']}>
        """
        token = self.read(7)
        if token != b'trailer':
            self.on_parser_error("trailer expected")
        self.maybe_spaces_or_comments()
        return Trailer(self.dictionary())

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

    def body_element(self):
        """
        Indirect object, startxref or trailer
        """
        if self.is_digit:
            obj = self.indirect_object()
        elif self.current == b's':
            obj = self.startxref()
        elif self.current == b't':
            obj = self.trailer()
        else:
            self.on_parser_error("Indirect object, startxref or trailer expected")
        return obj

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


class RegistryPDFParser(PDFParser):

    def __init__(self, fileobj, registry):
        super(RegistryPDFParser, self).__init__(fileobj)
        self.registry = registry

    def on_parsed_indirect_object(self, obj):
        self.registry.register(obj)

    def indirect_object(self):
        obj = super(RegistryPDFParser, self).indirect_object()
        # handle all known indirect objects
        self.on_parsed_indirect_object(obj)
        return obj


if __name__ == "__main__":
    import doctest
    doctest.testmod()
