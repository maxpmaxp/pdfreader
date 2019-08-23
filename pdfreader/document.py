import logging

from .exceptions import ParserException
from .registry import Registry
from .parser import RegistryPDFParser
from .types import null, IndirectObject, Stream, Array, Dictionary, IndirectReference, ATOMIC_TYPES

is_atomic = lambda obj: isinstance(obj, (ATOMIC_TYPES))


class PDFDocument(object):
    """ PDF document structure (how basic object types are used to represent PDF components:
        pages, fonts, annotations, images etc.) """

    def __init__(self, fobj):
        """ fobj - file-like object

import logging
#logging.basicConfig(filename='pdf.log', filemode='w')
#logging.getLogger().setLevel("INFO")

from pdfreader import PDFDocument
#fd = open('data/tyler-or-DocumentFragment.pdf','rb')
#fd = open('data/fw8ben.pdf','rb')
#fd = open('data/leesoil-cases-2.pdf','rb')
#fd = open('data/ohcrash-02-0005-02-multiunit.pdf','rb')
#fd = open('data/ohcrash-scanned-case-converted-image.pdf','rb')
#fd = open('data/PDF32000_2008.pdf','rb')
doc = PDFDocument(fd)


        """

        self.registry = Registry()
        self.parser = RegistryPDFParser(fobj, self.registry)

        self.header = self.parser.pdf_header()
        self.trailer = self.parser.pdf_trailer()

        # save initial state for brute-force objects lookup
        self.parser.reset(self.header.offset)
        self.brute_force_state = self.parser.get_state()

        # load XRef in-use objects
        for xref in self.trailer.xrefs:
            self._load_xref_in_use(xref)

        # load XRef compressed objects
        for xref in self.trailer.xrefs:
            self._load_xref_compressed(xref)

        # resolve indirect_links
        self.root = self.build(self.trailer.root)

    def build(self, obj, visited=None):
        """ replace all object references with objects
            leave loops as is
            works quite long
        """
        logging.debug("Buliding {}".format(obj))
        if visited is None:
            visited = []

        on_return = None
        if isinstance(obj, IndirectReference):
            if obj not in visited:
                visited.append(obj)
                on_return = visited.pop
                obj = self.obj_by_ref(obj)

        # resolve subsequent references for Arrays, Dictionaries and Streams
        if isinstance(obj, Array):
            obj = [(self.build(o, visited) if not is_atomic(o) else o) for o in obj]
        elif isinstance(obj, Dictionary):
            obj = {k: (self.build(o, visited) if not is_atomic(o) else o) for k, o in obj.items()}
        elif isinstance(obj, Stream):
            obj.dictionary = {k: (self.build(o, visited) if not is_atomic(o) else o)
                              for k, o in obj.dictionary.items()}
        elif isinstance(obj, IndirectObject):
            # normally this shouldn't happen, but ponentially we can build it
            logging.warning("Attempt to build an indirect object. Possibly a bug.")
            obj = self.build(obj.val, visited)

        if on_return:
            on_return()
        return obj

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
                logging.exception("!!!Failed to locate {} {}: assuming null".format(num, gen))
                self.registry.register(IndirectObject(num, gen, null))
                break
        obj = self.registry.get(num, gen)
        return obj

    def obj_by_ref(self, objref):
        return self.locate_object(objref.num, objref.gen)

    def next_brute_force_object(self):
        self.parser.set_state(self.brute_force_state)
        self.parser.maybe_spaces_or_comments()
        obj = self.parser.body_element() # can be either indirect object, startxref or trailer
        self.brute_force_state = self.parser.get_state() # save state for the next BF
        return obj
