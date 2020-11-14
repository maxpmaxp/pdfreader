
class PDFHeader(object):
    """ %PDF1.3 """
    def __init__(self, version, offset=None):
        self.version = version
        self.major, self.minor = self.version.split(".")
        self.offset = offset

    def __repr__(self):
        return "<PDF Header:v={self.version} (major={self.major}, minor={self.minor}), offset={self.offset})>"\
            .format(self=self)


class PDFTrailer(object):
    """
        trailer
            << /Size 22 .... >>
        startxref
        16354
        %%EOF

        or a trailer from a stream
    """
    def __init__(self, xrefs, **kwargs):
        self.xrefs = xrefs
        self.params = kwargs

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
        return self.params.get("ID") or self.params.get("Id")

    def __repr__(self):
        return "<PDF Trailer:xrefs={self.xrefs},root={self.root},info={self.info}>".format(self=self)



