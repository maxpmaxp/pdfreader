PDFDocument vs. SimplePDFViewer
===============================

*pdfreader* provides 2 different interfaces for PDFs:
  - :class:`~pdfreader.PDFDocument`
  - :class:`~pdfreader.SimplePDFViewer`

What is the difference?

:class:`~pdfreader.PDFDocument`:
  - knows nothing about interpretation of content-level PDF operators
  - knows all about PDF file and document structure (types, objects, indirect objects, references etc.)
  - can be used to access any document object: XRef table, DocumentCatalog, page tree nodes (aka Pages), binary
    streams like Font, CMap, Form, Page etc.
  - can be used to access raw objects content (raw page content stream for example)
  - has no graphical state

:class:`~pdfreader.SimplePDFViewer`:
  - uses :class:`~pdfreader.PDFDocument` as document navigation engine
  - can render document content properly decoding it and interpreting PDF operators
  - has graphical state

Use :class:`~pdfreader.PDFDocument`  to navigate document and access raw data.

Use :class:`~pdfreader.SimplePDFViewer` to extract content you see in your favorite viewer
(`Adobe Acrobat Reader <https://acrobat.adobe.com/us/en/acrobat/pdf-reader.html>`_, hehe :-).

Let's see several usecases.

.. toctree::
   :maxdepth: 3

   extract_image
   extract_page_text
   extract_form_text
   extract_cmap
   extract_fonts
   navigate_objects