import logging

from .exceptions import ParserException
from .registry import Registry
from .parsers import RegistryPDFParser
from .types import null, IndirectObject, Stream, Array, Dictionary, IndirectReference, obj_factory


class PDFDocument(object):
    """ Represents PDF document structure

        :param fobj: file-like object: binary file descriptor, BytesIO stream etc.

    """
    #: contains PDF file header data
    header = None
    #: contains PDF file trailer data
    trailer = None
    #: references to document's Catalog instance
    root = None

    def __init__(self, fobj):
        """ Constructor method
        """

        self.registry = Registry()
        self.parser = RegistryPDFParser(fobj, self.registry)
        self.header = self.parser.pdf_header()
        self.trailer = self.parser.pdf_trailer()

        # save initial state for brute-force objects lookup
        self.parser.reset(self.header.offset)
        self.brute_force_state = self.parser.get_state()

        #: references to document's Catalog instance
        self.root = self.obj_by_ref(self.trailer.root)

    def build(self, obj, visited=None, lazy=True):
        """ Resolves all indirect references for the object.

            :param obj: an object from the document
            :type obj: one of supported PDF types

            :param lazy: don't resolve subsequent  indirect references if True (default).
            :type lazy: bool

            :param visited: Shouldn't be used. Internal param containing already resolved objects
                            to not fall into infinite loops
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
        Locates an object by it's number and generation.

        Objects lookup order:
          #. Known objects in registry (located before)
          #. XRef tables lookups
          #. Brute-force reading objects one by one from file start

        :param num: object number
        :type num: int

        :param gen: object generation
        :type gen: int

        :return: instance of one of supported PDF types (incl. null object) if found, null object otherwise.
                 Doesn't resolve indirect references.
        """
        # locate in registry
        if self.registry.is_registered(num, gen):
            return self.registry.get(num, gen)

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
        """
        Yields document pages one by one.

        :return:  :class:`~pdfreader.types.objects.Page` generator.
        """
        return self.root.Pages.pages()


if __name__ == "__main__":
    import doctest
    doctest.testmod()

