import codecs

from . import winascii, standard, macroman, pdfdoc


def register_pdf_encodings():
    codecs.register(winascii.search)
    codecs.register(standard.search)
    codecs.register(macroman.search)
    codecs.register(pdfdoc.search)
