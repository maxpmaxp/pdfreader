from .filestructure import File


class Document(object):
    """ PDF document structure (how basic object types are used to represent PDF components:
        pages, fonts, annotations, images etc.) """

    def __init__(self, fobj):
        """ fobj - file-like object """

        self.file = File(fobj)