.. meta::
   :description: pdfreader - How to extract CMap
   :keywords: pdfreader,python,pdf,cmap,parse,extract,PDFDocument
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: pdfreader - How to extract CMap
   :og:description: Example: how to extract CMap data for a font from PDF file.
   :og:site_name: pdfreader docs
   :og:type: article

.. testsetup::

  from pdfreader import PDFDocument
  import pkg_resources, os.path
  samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  file_name = os.path.join(samples_dir, 'tutorial-example.pdf')


How to extract CMap for a font from PDF
=======================================

In this example we extract CMap data for a font from PDF file.

CMaps (Character Maps) are text files used in PDF to map character codes to character glyphs in CID fonts.
They come to PDF from PostScript.

Let's open a :download:`sample document <pdfs/tutorial-example.pdf>`.

.. doctest::

  >>> from pdfreader import PDFDocument
  >>> fd = open(file_name, "rb")
  >>> doc = PDFDocument(fd)

Now let's navigate to the 3rd page:

.. doctest::

  >>> from itertools import islice
  >>> page = next(islice(doc.pages(), 2, 3))

and check page's fonts.

  >>> page.Resources.Font
  {'R11': <IndirectReference:n=153,g=0>, ... 'R9': <IndirectReference:n=152,g=0>}
  >>> len(page.Resources.Font)
  9

We see 9 different font resources.
As *pdfreader* is a lazy reader the font data has not been read yet. We just see the names and
the references to the objects.

Let's have a look at font named `R26`.

.. doctest::

  >>> font = page.Resources.Font['R26']
  >>> font.Subtype, bool(font.ToUnicode)
  ('Type1', True)

It is PostScript Type1 font, and texts use CMap provided by `ToUnicode` attribute.
Font's `ToUnicode` attribute contains a reference to the CMap file data stream:

.. doctest::

  >>> cmap = font.ToUnicode

Cmap file is a :class:`~pdfreader.types.objects.StreamBasedObject` instance containing flate encoded binary stream.

.. doctest::

  >>> type(cmap)
  <class 'pdfreader.types.objects.StreamBasedObject'>
  >>> cmap.Filter
  'FlateDecode'

that can be decoded by accessing :attr:`~pdfreader.types.objects.StreamBasedObject.filtered`:

.. doctest::

  >>> data = cmap.filtered
  >>> data
  b'/CIDInit /ProcSet findresource ... end\n'
  >>> with open("sample-cmap.txt", "wb") as f:
  ...     f.write(data)
  229

Voila! `229` bytes written :-)

As it is a text file you can :download:`open it <downloads/sample-cmap.txt>` with your favorite text editor.

