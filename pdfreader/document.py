import logging
log = logging.getLogger(__name__)

from .registry import Registry
from .parsers import RegistryPDFParser
from .securityhandler import security_handler_factory
from .types import IndirectObject, Stream, Array, Dictionary, IndirectReference, obj_factory
from .utils import cached_property, from_pdf_datetime


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

        if self.encrypt:
            sec_handler = security_handler_factory(self.trailer.id, self.encrypt, password)
            self.parser.set_security_handler(sec_handler)

        self.root = self.obj_by_ref(self.trailer.root)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return

    @cached_property
    def encrypt(self):
        """
        Document's Encrypt dictionary (if present)

        :return: dict or None
        """
        res = None
        obj = self.trailer.encrypt
        if obj:
            res = self.locate_encrypt_by_ref(obj) if isinstance(obj, IndirectReference) else obj
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
        log.debug("Buliding {}".format(obj))
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
            log.warning("Attempt to build an indirect object. Possibly a bug.")
            obj = self.build(obj.val, visited, lazy)

        if on_return:
            on_return()
        return obj

    def locate_object(self, num, gen):
        return self.parser.locate_object(num, gen)

    def obj_by_ref(self, objref):
        obj = self.parser.locate_object(objref.num, objref.gen)
        return obj_factory(self, obj)

    def locate_encrypt_by_ref(self, objref):
        """ Locates Encrypt object by ref from a stream-style xref.
            In some cases for encrypted files this reference is missing from Xref table
            but the indirect object comes right before the xref stream.
        """
        obj = self.parser.locate_object_in_registry(objref.num, objref.gen) \
              or self.parser.locate_object_by_xref(objref.num, objref.gen) \
              or self.parser.locate_backwards_from_trailer(objref.num, objref.gen) \
              or self.parser.locate_object(objref.num, objref.gen)

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

    @property
    def metadata(self):
        """
        Returns document metadata from file's trailer info dict

        :return: dict, if metadata exists `None` otherwise.
        """
        res = None
        info = self.trailer.info
        if info:
            res = self.locate_object(info.num, info.gen)
            for k, v in res.items():
                if isinstance(v, bytes):
                    try:
                        res[k] = v.decode()
                        if k in ('CreationDate', 'ModDate'):
                            res[k] = from_pdf_datetime(res[k])
                    except (UnicodeDecodeError, ValueError, TypeError):
                        pass
        return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
