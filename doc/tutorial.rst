.. meta::
   :description: pdfreader tutorial - basic PDF parsing techniques: extract texts, images, accessing objects.
   :keywords: pdfreader,tutorial,parse,text,pdf,image,extract
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: pdfreader tutorial
   :og:description: pdfreader tutorial - basic PDF parsing techniques: extract texts, images, accessing objects.
   :og:site_name: pdfreader docs
   :og:type: article

Tutorial
========

.. testsetup::

  from pdfreader import PDFDocument
  import pkg_resources
  import pkg_resources, os.path
  samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  file_name = os.path.join(samples_dir, 'tutorial-example.pdf')
  protected_file_name = os.path.join(samples_dir, 'encrypted-with-qwerty.pdf')
  annotations_file_name = os.path.join(samples_dir, 'annot-sample.pdf')


Have a look at the :download:`sample file <examples/pdfs/tutorial-example.pdf>`.
In this tutorial we will learn simple methods on
- how to open it
- navigate pages
- exract images and texts.


Prerequisites
-------------
Before we start, let's make sure that you have the *pdfreader* distribution
:doc:`installed <installation>`. In the Python shell, the following
should run without raising an exception:

.. doctest::

  >>> import pdfreader
  >>> from pdfreader import PDFDocument, SimplePDFViewer


How to start
------------

*Note:* If you need to extract texts/images or other content from PDF you can skip
these chapters and go directly to :ref:`tutorial-content`.

The first step when working with *pdfreader* is to create a
:class:`~pdfreader.document.PDFDocument` instance from a binary file. Doing so is easy:

.. doctest::

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

.. _tutorial-document-catalog:

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


How to browse document pages
----------------------------

There is a generator :meth:`~pdfreader.document.PDFDocument.pages` to browse the pages one by one.
It yields :class:`~pdfreader.types.objects.Page` instances.

.. doctest::

  >>> page_one = next(doc.pages())

You may read all the pages at once

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

It's possible to access parent Pages Tree Node for the page, which is :class:`~pdfreader.types.objects.PageTreeNode`
instance, and all it's kids:

.. doctest::

  >>> page_six.Parent.Type
  'Pages'
  >>> page_six.Parent.Count
  15
  >>> len(page_six.Parent.Kids)
  15

Our example contains the only one Pages Tree Node. That is not always true.

For the complete list Page and Pages attributes see PDF-1.7 specification
`sections 7.7.3.2-7.7.3.3 <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=76>`_

.. _tutorial-content:

How to start extracting PDF content
-----------------------------------

It's possible to extract raw data with :class:`~pdfreader.document.PDFDocument` instance but it just represents raw
document structure. It can't interpret PDF content operators, that's why it might be hard.

Fortunately there is :class:`~pdfreader.viewer.SimplePDFViewer`, which understands a lot.
It is a simple PDF interpreter which can "display" (whatever this means)
a page on :class:`~pdfreader.viewer.SimpleCanvas`.

.. doctest::

  >>> fd = open(file_name, "rb")
  >>> viewer = SimplePDFViewer(fd)

The viewer instance gets content you see in your Adobe Acrobat Reader.
:class:`~pdfreader.viewer.SimplePDFViewer` provides you with :class:`~pdfreader.viewer.SimpleCanvas` objects
for every page. This object contains page content: images, forms, texts.

The code below walks through all document's pages and extracts data:

.. doctest::

  >>> for canvas in viewer:
  ...     page_images = canvas.images
  ...     page_forms = canvas.forms
  ...     page_text = canvas.text_content
  ...     page_inline_images = canvas.inline_images
  ...     page_strings = canvas.strings
  >>>

Also you can navigate to some specific page with
:meth:`~pdfreader.viewer.SimplePDFViewer.navigate` and call :meth:`~pdfreader.viewer.SimplePDFViewer.render`

.. doctest::

  >>> viewer.navigate(8)
  >>> viewer.render()
  >>> page_8_canvas = viewer.canvas

The viewer extracts:
  - page images (XObject)
  - page inline images (BI/ID/EI operators)
  - page forms (XObject)
  - decoded page strings (PDF encodings & CMap support)
  - human (and robot) readable page markdown - original PDF commands containing decoded strings.

.. _tutorial-images:

Extracting Page Images
----------------------

There are 2 kinds of images in PDF documents:
    - XObject images
    - inline images

Every one is represented by its own class
(:class:`~pdfreader.types.objects.Image` and :class:`~pdfreader.types.content.InlineImage`)

Let's extract some pictures now! They are accessible through :attr:`~pdfreader.viewer.SimplePDFViewer.canvas`
attribute. Have a look at `page 8  <examples/pdfs/tutorial-example.pdf#page=8>`_
of the sample document. It contains a fax message, and is is available
on :attr:`~pdfreader.viewer.SimpleCanvas.inline_images` list.

.. doctest::

  >>> len(viewer.canvas.inline_images)
  1
  >>> fax_image = viewer.canvas.inline_images[0]
  >>> fax_image.Filter
  'CCITTFaxDecode'
  >>> fax_image.Width, fax_image.Height
  (1800, 3113)

This would be nothing if you can't see the image itself :-)
Now let's convert it to a `Pillow/PIL Image <https://pillow.readthedocs.io/en/stable/reference/Image.html>`_
object and save!

.. doctest::

  >>> pil_image = fax_image.to_Pillow()
  >>> pil_image.save('fax-from-p8.png')

Voila! Enjoy opening it in your favorite editor!

Check the complete list of `Image (sec. 8.9.5) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=206>`_
and `InlineImage (sec. 8.9.7) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=214>`_
attributes.


.. _tutorial-texts:

Extracting texts
----------------

Getting texts from a page is super easy. They are available on :attr:`~pdfreader.viewer.SimpleCanvas.strings` and
:attr:`~pdfreader.viewer.SimpleCanvas.text_content` attributes.

Let's go to the previous page (`#7  <examples/pdfs/tutorial-example.pdf#page=7>`_) and extract some data.

.. doctest::

  >>> viewer.prev()


Remember, when you navigate another page the viewer resets the canvas.

.. doctest::

  >>> viewer.canvas.inline_images == []
  True

Let's render the page and see the texts.
  - Decoded plain text strings are on :attr:`~pdfreader.viewer.SimpleCanvas.strings`
    (by pieces and in order they come on the page)
  - Decoded strings with PDF markdown are on :attr:`~pdfreader.viewer.SimpleCanvas.text_content`

.. doctest::

  >>> viewer.render()
  >>> viewer.canvas.strings
  ['P', 'E', 'R', 'S', 'O', 'N', 'A', 'L', ... '2', '0', '1', '7']

As you see every character comes as an individual string in the page content stream here. Which is not usual.

Let's go to the very `first page  <examples/pdfs/tutorial-example.pdf#page=1>`_

.. doctest::

  >>> viewer.navigate(1)
  >>> viewer.render()
  >>> viewer.canvas.strings
  [' ', 'P', 'l', 'a', 'i', 'nt', 'i', 'f', 'f', ... '10/28/2019 1:49 PM', '19CV47031']

PDF markdown is also available.

.. doctest::

  >>> viewer.canvas.text_content
  "\n BT\n0 0 0 rg\n/GS0 gs... ET"


And the strings are decoded properly. Have a look at
:download:`the file <examples/downloads/tutorial-sample-content-stream-p1.txt>`:

.. doctest::

  >>> with open("tutorial-sample-content-stream-p1.txt", "w") as f:
  ...     f.write(viewer.canvas.text_content)
  19339


*pdfreader* takes care of decoding binary streams, character encodings, CMap, fonts etc.
So finally you have human-readable content sources and markdown.


Hyperlinks and annotations
--------------------------

Let's Have a look at the :download:`sample file <examples/pdfs/annot-sample.pdf>`.

.. doctest::

  >>> fd = open(annotations_file_name, "rb")
  >>> viewer = SimplePDFViewer(fd)
  >>> viewer.navigate(1)
  >>> viewer.render()

It contains several hyperlinks. Let's extract them!

Unlike HTML, PDF links are rectangle parts of viewing area, they are neither text properties nor attributes.
That's why you can't find linked URLs in text content:

.. doctest::

  >>> plain_text = "".join(viewer.canvas.strings)
  >>> "http" in plain_text
  False

Links can be found in `:class:`~pdfreader.types.objects.Page` annotations
(see `12.5 Annotations <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=389>`_),
which help user to interact with document.

Annotations for a current page are accessible through :meth:`~pdfreader.viewer.SimplePDFViewer.annotations`.
The sample document has 3 annotations:

.. doctest::

  >>> len(viewer.annotations)
  3

There are different types of annotations. Hyperlinks have `Subtype` of `Link`. We're ready to extract URLs:

.. doctest::

  >>> links = [annot.A.URI for annot in viewer.annotations
  ...          if annot.Subtype == 'Link']
  >>> links
  [b'http://www.apple.com', b'http://example.com', b'mailto:example@example.com']


Encrypted and password-protected PDF files
------------------------------------------

What if your file is protected by a password? Not a big deal! *pdfreader* supports encrypted and password-protected files!
Just specify the password when create :class:`~pdfreader.document.PDFDocument` or
:class:`~pdfreader.viewer.SimplePDFViewer`.

Let's see how this works with an encrypted password-protected file
:download:`sample file <examples/pdfs/encrypted-with-qwerty.pdf>`.
The password is *qwerty*.

.. doctest::

   >>> fd = open(protected_file_name, "rb")
   >>> viewer = SimplePDFViewer(fd, password="qwerty")
   >>> viewer.render()
   >>> text = "".join(viewer.canvas.strings)
   >>> text
   'Sed ut perspiciatis unde omnis iste ... vel illum qui dolorem eum fugiat quo voluptas nulla pariatur?'

The same about :class:`~pdfreader.document.PDFDocument`:

.. doctest::

   >>> fd = open(protected_file_name, "rb")
   >>> doc = PDFDocument(fd, password="qwerty")
   >>> page_one = next(doc.pages())
   >>> page_one.Contents
   <Stream:len=1488,data=b'...'>


What if the password is wrong? It throws an exception.

.. doctest::

   >>> fd = open(protected_file_name, "rb")
   >>> doc = PDFDocument(fd, password="wrong password")
   Traceback (most recent call last):
   ...
   ValueError: Incorrect password

The same for :class:`~pdfreader.viewer.SimplePDFViewer`:

.. doctest::

   >>> fd = open(protected_file_name, "rb")
   >>> doc = SimplePDFViewer(fd, password="wrong password")
   Traceback (most recent call last):
   ...
   ValueError: Incorrect password

*Note:* Do you know, that PDF format supports encrypted files protected by the default empty password?
Despite the password is empty, such files are encrypted still. Fortunately, *pdfreader* detects end decrypts such files
automatically, there is nothig special to do!