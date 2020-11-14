import logging

from .registry import Registry
from .parsers import RegistryPDFParser
from .securityhandler import security_handler_factory
from .types import IndirectObject, Stream, Array, Dictionary, IndirectReference, obj_factory
from .utils import cached_property


class PDFDocument(object):
    """
    Represents PDF document structure

    :param fobj: file-like object: binary file descriptor, BytesIO stream etc.
    :param password: Optional. Password to access PDF content. Defaults to the empty string.

    """
    #: contains PDF file header data
    header = None
    #: contains PDF file trailer data
    trailer = None
    #: references to document's Catalog instance
    root = None

    def __init__(self, fobj, password=''):
        """ Constructor method
        """

        self.registry = Registry()

        self.parser = RegistryPDFParser(fobj, self.registry)
        self.header = self.parser.header
        self.trailer = self.parser.trailer

        if self.encrypt and self.encrypt.Filter != "Standard":
            raise ValueError("Unsupported encryption handler {}".format(self.encrypt.Filter))

        self.root = self.obj_by_ref(self.trailer.root)

        if self.encrypt:
            sec_handler = security_handler_factory(self.trailer.id, self.encrypt, password)
            self.parser.set_security_handler(sec_handler)

    @cached_property
    def encrypt(self):
        """
        Document's Encrypt dictionary (if present)

        :return: dict or None
        """
        res = None
        obj = self.trailer.encrypt
        if obj:
            res = self.obj_by_ref(obj) if isinstance(obj, IndirectReference) else obj
        return res

    def build(self, obj, visited=None, lazy=True):
        """
        Resolves all indirect references for the object.

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
        return self.parser.locate_object(num, gen)

    def obj_by_ref(self, objref):
        obj = self.parser.locate_object(objref.num, objref.gen)
        return obj_factory(self, obj)

    def deep_obj_by_ref(self, obj, maxdepth=100):
        counter = maxdepth
        while isinstance(obj, IndirectObject) and counter:
            obj = self.obj_by_ref(obj)
            counter -= 1

        if isinstance(obj, IndirectObject):
            raise ValueError("Max reference depth exceeded")
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

