.. meta::
   :description: pdfreader  - PDFDocument vs. SimplePDFViewer
   :keywords: pdfreader,PDFDocument,SimplePDFViewer,pdf
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: pdfreader - PDFDocument vs. SimplePDFViewer
   :og:description: pdfreader - choosing right method PDFDocument vs. SimplePDFViewer
   :og:site_name: pdfreader docs
   :og:type: article

PDFDocument vs. SimplePDFViewer
===============================

*pdfreader* provides 2 different interfaces for PDFs:
  - :class:`~pdfreader.document.PDFDocument`
  - :class:`~pdfreader.viewer.SimplePDFViewer`

What is the difference?

:class:`~pdfreader.document.PDFDocument`:
  - knows nothing about interpretation of content-level PDF operators
  - knows all about PDF file and document structure (types, objects, indirect objects, references etc.)
  - can be used to access any document object: XRef table, DocumentCatalog, page tree nodes (aka Pages), binary
    streams like Font, CMap, Form, Page etc.
  - can be used to access raw objects content (raw page content stream for example)
  - has no graphical state

:class:`~pdfreader.viewer.SimplePDFViewer`:
  - uses :class:`~pdfreader.document.PDFDocument` as document navigation engine
  - can render document content properly decoding it and interpreting PDF operators
  - has graphical state

Use :class:`~pdfreader.document.PDFDocument`  to navigate document and access raw data.

Use :class:`~pdfreader.viewer.SimplePDFViewer` to extract content you see in your favorite viewer
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