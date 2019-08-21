from typing import List

from .types import IndirectObject, ObjRef
from .xref import XRef


class Header(object):
    """ %PDF1.3 """
    def __init__(self, version, offset=None):
        self.version = str(version)
        self.major, self.minor = self.version.split(".")
        self.offset = offset

    def __repr__(self):
        return "<PDF Header:v={self.version} (major={self.major}, minor={self.minor})>".format(self=self)


Body = List[IndirectObject]


class Trailer(object):
    """
        trailer
            << /Size 22 .... >>
        startxref
        16354
        %%EOF
    """
    def __init__(self, xref, **kwargs):
        assert isinstance(xref, XRef)
        self.xref = xref
        self.params = kwargs

    @property
    def prev(self):
        """ Previous cross-reference section offset.
            if a document contains incremental updates and more than one xref section.
        """
        return self.params.get("Prev")

    @property
    def root(self):
        """ Root """
        return self.params["Root"]

    @property
    def encrypt(self):
        """ Document encryptio dictionary if exists """
        return self.params.get("Encrypt")

    @property
    def info(self):
        """ Document info dictionary if exists """
        return self.params.get("Info")

    @property
    def id(self):
        """ Array of two strings containing a file identifier if exists """
        return self.params.get("Id")

    def __repr__(self):
        return "<PDF Trailer:xref=<{self.xref_offset},{self.xref_size}>,root={self.root}>"


class File(object):
    """ PDF File structure (how objects are stored, accessed and updated).
        Semantically independent.
    """

    def __init__(self, fobj):
        """ fobj - file-like object """
        # Todo:
        # 1. Read header & ensure it is PDF
        # 2. Read Trailer
        # 3. Read all Cross References
        # 4. Read all in-use objects (lazy)

