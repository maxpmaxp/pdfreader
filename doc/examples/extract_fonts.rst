How to extract Font data from PDF
=================================

In this example we extract font data from a PDF file.

Let's open a :download:`sample document <pdfs/example-font.pdf>`.

.. doctest::

  >>> from pdfreader import PDFDocument
  >>> import pkg_resources, os.path
  >>> samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  >>> file_name = os.path.join(samples_dir, 'example-font.pdf')
  >>> fd = open(file_name, "rb")
  >>> doc = PDFDocument(fd)

Now let's see what fonts the very first page uses:

.. doctest::

  >>> page = next(doc.pages())
  >>> page.Resources.Font
  {'T1_0': <IndirectReference:n=22,g=0>, ... <IndirectReference:n=41,g=0>}


We see 5 fonts named `T1_0`, `T1_1`, `T1_2`, `TT0` and `TT1`.
As *pdfreader* is a lazy reader the font data has not been read yet. We just see the names and
the references to the objects.

Let's have a look at font `T1_0`.

.. doctest::

  >>> font = page.Resources.Font['T1_0']
  >>> font.Subtype, font.BaseFont, font.Encoding
  ('Type1', 'SCMYNU+TimesNewRomanPSMT', 'WinAnsiEncoding')

It is PostScript Type1 font, based on TimesNewRomanPSMT. Texts use `WinAnsiEncoding`, which is almost like
python's `cp1252`.

Font's `FontDescriptor` contains a reference to the font file data stream:

.. doctest::

  >>> font_file = font.FontDescriptor.FontFile

The font file is a flate encoded binary stream :class:`~pdfreader.types.objects.StreamBasedObject`

.. doctest::

  >>> type(font_file)
  <class 'pdfreader.types.objects.StreamBasedObject'>
  >>> font_file.Filter
  ['FlateDecode']

which can be decoded by accessing :attr:`~pdfreader.types.objects.StreamBasedObject.filtered`

.. doctest::

  >>> data = font_file.filtered
  >>> with open("sample-font.type1", "wb") as f:
  ...     f.write(data)
  16831

Voila! `16831` bytes written :-)

