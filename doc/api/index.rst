pdfreader API
=============

.. toctree::

   document
   viewer
   types


.. automodule:: pdfreader
   :synopsis: Pythonic API for PDF documents

   .. autodata:: version

   Navigating and interpreting PDF documents:

   .. data:: PDFDocument

      Alias for :class:`pdfreader.document.PDFDocument`

   .. data:: SimplePDFViewer

      Alias for :class:`pdfreader.viewer.SimplePDFViewer`


   Major classes used by :class:`pdfreader.viewer.SimplePDFViewer`

      - :class:`pdfreader.viewer.SimpleCanvas`
      - :class:`pdfreader.viewer.Resources`
      - :class:`pdfreader.viewer.GraphicsState`
      - :class:`pdfreader.viewer.GraphicsStateStack`


   Major classes and types:

      - :class:`pdfreader.types.objects.StreamBasedObject`
      - :class:`pdfreader.types.objects.DictBasedObject`
      - :class:`pdfreader.types.objects.ArrayBasedObject`
      - :class:`pdfreader.types.objects.Catalog`
      - :class:`pdfreader.types.objects.Page`
      - :class:`pdfreader.types.objects.PageTreeNode`
      - :class:`pdfreader.types.objects.Image`

   Objects you face up in page/form content streams:

      - :class:`pdfreader.types.content.InlineImage`
      - :class:`pdfreader.types.content.Operator`
