from .codecs import register_pdf_encodings
from .document import PDFDocument
from .viewer import SimplePDFViewer, PageDoesNotExist

register_pdf_encodings()

#: package version
__version__ = version = '0.1.15'
