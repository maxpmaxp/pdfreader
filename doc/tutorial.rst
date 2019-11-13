Tutorial
========

.. testsetup::

  from pdfreader import PDFDocument
  import pkg_resources

Have a look at the :download:`sample file <examples/pdfs/tutorial-example.pdf>`.
In this tutorial we will learn simple methods on
- how to open it
- navigate pages
- exract images and texts.


Prerequisites
-------------
Before we start, let's make sure that you have the **pdfreader** distribution
:doc:`installed <installation>`. In the Python shell, the following
should run without raising an exception:

.. doctest::

  >>> import pdfreader
  >>> from pdfreader import PDFDocument


How to start
------------

The first step when working with **pdfreader** is to create a
:class:`~pdfreader.document.PDFDocument` instance from a binary file. Doing so is easy:

.. doctest::

  >>> from pdfreader import PDFDocument
  >>> import pkg_resources, os.path
  >>> samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  >>> file_name = os.path.join(samples_dir, 'tutorial-example.pdf')
  >>> fd = open(file_name, "rb")
  >>> doc = PDFDocument(fd)

As *pdfreader* implements lazy PDF reading (it never reads more then you ask from the file),
so it's important to keep the file opened while you are working with the document.
Make sure you don't close it until you're done.

It is also possible to use a binary file-like object to create an instance, for example:

.. doctest::

  >>> from io import BytesIO
  >>> with open(file_name, "rb") as f:
  ...     stream = BytesIO(f.read())
  >>> doc2 = PDFDocument(stream)

Let's check the PDF version of the document

.. doctest::

  >>> doc.header.version
  '1.6'

Now we can go ahead to the document catalog and walking through pages.

How to access Document Catalog
------------------------------

:class:`~pdfreader.types.objects.Catalog` (aka Document Root) contains all you need to know to start working with
the document: metadata, reference to pages tree, layout, outlines etc.

.. doctest::

  >>> doc.root.Type
  'Catalog'
  >>> doc.root.Metadata.Subtype
  'XML'
  >>> doc.root.Outlines.First['Title']
  b'Start of Document'


For the full list of document root attributes see PDF-1.7 specification
`section 7.7.2 <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=73>`_


How to walk document pages
--------------------------

There is a generator :meth:`~pdfreader.document.PDFDocument.pages` to walk the pages one by one.
It yields :class:`~pdfreader.types.objects.Page` instances.

.. doctest::

  >>> page_one = next(doc.pages())

You may also want to read all the pages at once

.. doctest::

  >>> all_pages = [p for p in doc.pages()]
  >>> len(all_pages)
  15

Now we know how many pages are there!

You may wish to get some specific page if your document contains hundreds and thousands.
Doing this is just a little bit trickier.
To get the 6th page you need to walk through the previous five.

.. doctest::

  >>> from itertools import islice
  >>> page_six = next(islice(doc.pages(), 5, 6))
  >>> page_five = next(islice(doc.pages(), 4, 5))

Don't forget, that all PDF viewers start page numbering from 1,
however Python lists start their indexes from 0.

.. doctest::

  >>> page_eight = all_pages[7]

Now we can access all page attributes:

.. doctest::

  >>> page_six.MediaBox
  [0, 0, 612, 792]
  >>> page_six.Annots[0].Subj
  b'Text Box'

It's possible to access parent Pages Tree Node for the page, aka :class:`~pdfreader.types.objects.Pages` instance
and all it's kids:

.. doctest::

  >>> page_six.Parent.Type
  'Pages'
  >>> page_six.Parent.Count
  15
  >>> len(page_six.Parent.Kids)
  15

By accident our example contains the only one Pages Tree Node, which is not always true.

For the complete list Page and Pages attributes see PDF-1.7 specification
`sections 7.7.3.2-7.7.3.3 <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=76>`_

.. _tutorial-images:

Extracting Page Images
----------------------

There are 2 kinds of images in PDF documents:
    - XObject images
    - inline images

Every kind has its own class
(:class:`~pdfreader.types.objects.Images` and :class:`~pdfreader.types.content.InlineImage`)
and generators: :meth:`~pdfreader.types.objects.Page.images` and :meth:`~pdfreader.types.objects.Page.inline_images`

Let's extract some pictures now!

.. doctest::

  >>> fax_image = next(page_eight.inline_images())
  >>> fax_image.Filter
  'CCITTFaxDecode'
  >>> fax_image.Width, fax_image.Height
  (1800, 3113)

This would be nothing if you can't see the image itself :-)
Fortunately we can convert it to a `Pillow/PIL Image <https://pillow.readthedocs.io/en/stable/reference/Image.html>`_
object and save!

.. doctest::

  >>> pil_image = fax_image.to_Pillow()
  >>> pil_image.save('fax-from-p8.png')

Voila! Enjoy opening it in your favorite editor!

Check the complete list of `Image (sec. 8.9.5) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=206>`_
and `InlineImage (sec. 8.9.7) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=214>`_
attributes.


Extracting texts
----------------

Getting texts from a page is super easy. Just call :meth:`~pdfreader.types.objects.Page.text` to get plain texts.

.. doctest::

  >>> page_one.text()
  " Plaintiff’s Complaint ... 1:49 PM19CV47031"

If you wish to see the markdown of all BT/ET blocks and other PDF commands (you may need this for further parsing),
just run :meth:`~pdfreader.types.objects.Page.text_sources`:

.. doctest::

  >>> print(page_one.text_sources())
  BT
  0 0 0 rg
  /GS0 gs
  /T1_0 9.96001 Tf
  ...
  22.35001 -13.79883 Td
  (19CV47031)Tj
  ET


*pdfreader* takes care of decoding binary streams, character encodings, CMap, fonts etc.
So finally you have human-readable texts and markdown.
