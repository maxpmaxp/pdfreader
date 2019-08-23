from .exceptions import ParserException
from .registry import Registry
from .parser import PDFParser
from .types import null, IndirectObject, Stream


class PDFDocument(object):
    """ PDF document structure (how basic object types are used to represent PDF components:
        pages, fonts, annotations, images etc.) """

    def __init__(self, fobj):
        """ fobj - file-like object

from pdfreader.parser import PDFParser
fd = open('data/tyler-or-DocumentFragment.pdf','rb')

p = PDFParser(fd).parse()


        """
        self.parser = PDFParser(fobj)

        self.registry = Registry()
        self.parser.on_parsed_indirect_object = self.registry.register

        self.header = self.parser.pdf_header()
        self.trailer = self.parser.pdf_trailer()

        self.next_brute_force_offset = self.header.offset

        # load XRef in-use objects
        for xref in self.trailer.xrefs:
            self._load_xref_in_use(xref)

        # load XRef compressed objects
        for xref in self.trailer.xrefs:
            self._load_xref_compressed(xref)

    def _load_xref_in_use(self, xr):
        # load in_use objects
        for xre in xr.in_use.values():
            try:
                self.parser.reset(xre.offset)
                self.parser.indirect_object()
            except ParserException:
                pass

    def _load_xref_compressed(self, xr):
        # load in_use objects
        for xre in xr.compressed.values():
            _ = self.locate_object(xre.number, 0)

    def locate_object(self, num, gen):
        while not self.registry.is_registered(num, gen):
            try:
                _ = self.next_brute_force_object()
            except ParserException:
                # treat not-found objects as nulls
                self.registry.register(IndirectObject(num, gen, null))
                break
        obj = self.registry.get(num, gen)
        return obj

    def next_brute_force_object(self):
        self.parser.reset(self.next_brute_force_offset)
        self.parser.maybe_spaces_or_comments()
        obj = self.parser.indirect_object()
        self.next_brute_force_offset = self.parser.current_stream_offset
        return obj
