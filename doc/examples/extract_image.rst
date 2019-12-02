.. meta::
   :description: pdfreader - How to extract images from PDF
   :keywords: pdfreader,python,pdf,image,inline,xobject,mask,parse,extract,SimplePDFViewer
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: pdfreader - How to extract images from PDF
   :og:description: Real-life examples on extracting inline images, XObjects and image masks from PDF.
   :og:site_name: pdfreader docs
   :og:type: article

.. testsetup::

  from pdfreader import PDFDocument, SimplePDFViewer
  import pkg_resources, os.path
  samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  file_name = os.path.join(samples_dir, 'example-image-xobject.pdf')
  pdf_file_name = os.path.join(samples_dir, 'tutorial-example.pdf')


How to extract XObject or Inline Images, Image Masks
====================================================

Extracting Inline Images is discussed in tutorial :ref:`tutorial-images`,
so let's focus on XObject Images and Image Masks.

Extracting XObject Image
------------------------

Open a sample document.

.. doctest::

  >>> from pdfreader import PDFDocument
  >>> fd = open(file_name, "rb")
  >>> doc = PDFDocument(fd)

Have a look at the sample file :download:`sample file <pdfs/example-image-xobject.pdf>`.
There is a logo on the first page. Let's extract it.

.. doctest::

 >>> page = next(doc.pages())

Let's check a dictionary of XObject resources for the page:

.. doctest::

  >>> page.Resources.XObject
  {'img0': <IndirectReference:n=11,g=0>}

This stands for an XObject named `img0`, and referenced under number 11 and generation 0.
The object has not been read by *pdfreader* still. We are lazy readers. We read objects only when we need them.
Let's see what the object is.

.. doctest::

  >>> xobj = page.Resources.XObject['img0']

We just read the object (`__getitem__` does this implicitly) and now we may access its attributes.

.. doctest::

  >>> xobj.Type, xobj.Subtype
  ('XObject', 'Image')

Wow! It's really an image. Should we care about it's internal PDF representation?
Of course no, let's just convert it to
a `Pillow/PIL Image <https://pillow.readthedocs.io/en/stable/reference/Image.html>`_ and save.

.. doctest::

  >>> pil_image = xobj.to_Pillow()
  >>> pil_image.save("extract-logo.png")

And here we are!

.. image:: img/example-logo.png

Try to open it and see any differences. It's absolutely the same as in the document.

Now you can manipulate `pil_image` with usual PIL methods: rotate, convert, blur, split, inverse, merge
and so on, so on, so on.

Extracting Images: a very simple way
------------------------------------

A very simple way also exisits.
Use :class:`~pdfreader.viewer.SimplePDFViewer`:

.. doctest::

   >>> from pdfreader import SimplePDFViewer
   >>> fd = open(file_name, "rb")
   >>> viewer = SimplePDFViewer(fd)
   >>> viewer.render()

After rendering all 1st page images are on the canvas

.. doctest::

   >>> all_page_images = viewer.canvas.images
   >>> all_page_inline_images = viewer.canvas.inline_images
   >>> img = all_page_images['img0']
   >>> img.Type, img.Subtype
   ('XObject', 'Image')

Now you can convert it with magic :meth:`~pdfreader.types.objects.Image.to_Pillow` method, save or do whatever you want!

Extracting Image Masks
----------------------

Image Mask is just a specific kind of image actually. Except it is not always visible directly in your PDF Viewer.
Nevertheless it can be accessed absolutely the same way.

Let's have a look at the :download:`example <pdfs/tutorial-example.pdf>` from :ref:`tutorial-images`,
and see what image masks it contains.

.. doctest::

  >>> from pdfreader import SimplePDFViewer
  >>> fd = open(pdf_file_name, "rb")
  >>> viewer = SimplePDFViewer(fd)

We use `Image.ImageMask` attribute to filter image masks from another images.
Let's go to the 5th page and take the first image mask:

.. doctest::

  >>> viewer.navigate(5)
  >>> viewer.render()
  >>> inline_images = viewer.canvas.inline_images
  >>> image_mask = next(img for img in inline_images if img.ImageMask)

Now convert it to Pillow object and save:

.. doctest::

  >>> pil_img = image_mask.to_Pillow()
  >>> pil_img.save("mask.png")

Have a look! What a beautiful QR-code!

.. image:: img/example-image-mask.png


Useful links
------------

You find the complete list of PDF image attributes in the specification:
  - `Image (sec. 8.9.5) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=206>`_
  - `InlineImage (sec. 8.9.7) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=214>`_

