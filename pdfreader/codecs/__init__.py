import codecs

from . import winascii, standard, macroman, pdfdoc


def register_pdf_encodings():
    codecs.register(winascii.WinAsciiCodec.search)
    codecs.register(standard.StandardCodec.search)
    codecs.register(macroman.MacRomanCodec.search)
    codecs.register(pdfdoc.PdfDocCodec.search)
