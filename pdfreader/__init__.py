from .codecs import register_pdf_encodings
from .document import PDFDocument
from .types import PDFHeader, PDFTrailer
from .registry import Registry
from pdfreader.types.xref import XRefEntry, CompressedObjEntry, XRef

register_pdf_encodings()

__version__ = version = '0.1.2'