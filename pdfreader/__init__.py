from .codecs import register_pdf_encodings
from .document import PDFDocument
from .viewer import SimplePDFViewer

register_pdf_encodings()

__version__ = version = '0.1.2'
