import logging

from .exceptions import ParserException
from .registry import Registry
from .parsers import RegistryPDFParser
from .types import null, IndirectObject, Stream, Array, Dictionary, IndirectReference, ATOMIC_TYPES, obj_factory


is_atomic = lambda obj: isinstance(obj, (ATOMIC_TYPES))


class PDFDocument(object):
    """ PDF document structure (how basic object types are used to represent PDF components:
        pages, fonts, annotations, images etc.) """

    def __init__(self, fobj):
        """ fobj - file-like object

            >>> import pkg_resources
            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/cumberland-arrests.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            31
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            30
            >>> text_objects[0].source
            'BT /Font-1 8 Tf 1 0 0 1 54 56.099998 Tm[(rpjlasr) 55(.x7) -32000  -23695.125 (07/29/19)] TJ\\n  ET'
            >>> text_objects[0].strings
            ['rpjlasr', '.x7', '07/29/19']

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/leesoil-cases-2.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            4
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            1
            >>> text_objects[0].strings[:7]
            ['LEE COUNTY JAIL', 'NEWS RELEASE', 'AS OF: 3/9/2019', 'Date of', ' ', 'Arrest', ': 3/9/2019  12:30:51AM']

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/ohcrash-02-0005-02-multiunit.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            5
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            346
            >>> text_objects[0].strings
            ['LOCAL INFORMATION']

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/ohcrash-scanned-case-converted-image.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            5
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            0

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/seattlemuni-cr-charges-brackets.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            4
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            11
            >>> text_objects[0].strings
            ['MUNICIPAL COURT OF SEATTLE DOCKET']

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/tyler-or-DocumentFragment.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            2
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            208
            >>> text_objects[0].source
            'BT\\n/GS0 gs\\n/TT0 9.96001 Tf\\n72.024 747.6 Td\\n( )Tj\\nET'

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/bellerica-pd-logs.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            1
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            2
            >>> text_objects[1].strings[:10]
            ['W', 'ARRAN', 'T', ' ', 'ARRES', 'T', '  -', 'Name:', '  CIANO, ', 'STEVEN MICHAE']

            >>> fd = pkg_resources.resource_stream('pdfreader', 'samples/waltham-pd-logs.pdf')
            >>> doc = PDFDocument(fd)
            >>> pages = [p for p in doc.pages()]
            >>> len(pages)
            9
            >>> text_objects = [to for to in pages[0].text_objects()]
            >>> len(text_objects)
            4
            >>> text_objects[0].strings
            ['QuickSearch Results', 'aaa.htm', '[8/26/2019 2:07:16 PM]']

        """

        self.registry = Registry()
        self.parser = RegistryPDFParser(fobj, self.registry)

        self.header = self.parser.pdf_header()
        self.trailer = self.parser.pdf_trailer()

        # save initial state for brute-force objects lookup
        self.parser.reset(self.header.offset)
        self.brute_force_state = self.parser.get_state()
        self.root = self.obj_by_ref(self.trailer.root)

    def build(self, obj, visited=None, lazy=True):
        """ replace all object references with objects
            If lazy=False doesn't build subsequent streams
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
            obj = [self.build(o, visited, lazy) for o in obj]
        elif isinstance(obj, Dictionary):
            if not lazy:
                obj = {k: self.build(o, visited, lazy) for k, o in obj.items()}
            obj = obj_factory(self, obj)
        elif isinstance(obj, Stream):
            if not lazy:
                obj.dictionary = {k: (self.build(o, visited, lazy)) for k, o in obj.dictionary.items()}
            obj = obj_factory(self, obj)
        elif isinstance(obj, IndirectObject):
            # normally this shouldn't happen, but ponentially we can build it
            logging.warning("Attempt to build an indirect object. Possibly a bug.")
            obj = self.build(obj.val, visited, lazy)

        if on_return:
            on_return()
        return obj

    def locate_object(self, num, gen):
        """
        Object lookup order:
        1. Known objects in registry
        2. XRefs - try to find and load
        3. Brute-force reading objects one by one from the file start
        """
        # Locate by xref
        for xref in self.trailer.xrefs:
            # try to find in-use object
            xre = xref.in_use.get(num)
            if xre and xre.generation == gen:
                try:
                    self.parser.reset(xre.offset)
                    self.parser.indirect_object()
                except ParserException:
                    pass
                if self.registry.is_registered(num, gen):
                    break
            # Try to find a compressed object
            xre = xref.compressed.get(num)
            if xre and xre.generation == gen:
                # Need to locate Object Stream in order to locate a compressed object
                self.locate_object(xre.number, xre.generation)
                if self.registry.is_registered(num, gen):
                    break

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
        obj = self.locate_object(objref.num, objref.gen)
        return obj_factory(self, obj)

    def deep_obj_by_ref(self, obj, maxdepth=100):
        counter = maxdepth
        while isinstance(obj, IndirectObject) and counter:
            obj = self.obj_by_ref(obj)
            counter -= 1

        if isinstance(obj, IndirectObject):
            raise ValueError("Max reference depth exceeded")
        return obj

    def next_brute_force_object(self):
        self.parser.set_state(self.brute_force_state)
        self.parser.maybe_spaces_or_comments()
        obj = self.parser.body_element() # can be either indirect object, startxref or trailer
        self.brute_force_state = self.parser.get_state() # save state for the next BF
        return obj

    def pages(self):
        return self.root.Pages.pages()


if __name__ == "__main__":
    import doctest
    doctest.testmod()

