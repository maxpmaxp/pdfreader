import codecs

from . import winansi, standard, macroman, pdfdoc


def register_pdf_encodings():
    codecs.register(winansi.WinAnsiCodec.search)
    codecs.register(standard.StandardCodec.search)
    codecs.register(macroman.MacRomanCodec.search)
    codecs.register(pdfdoc.PdfDocCodec.search)



