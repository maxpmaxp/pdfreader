.. meta::
   :description: pdfreader - How to browse PDF objects
   :keywords: pdfreader,python,pdf,objects,browse,parse,extract,raw,data,generation,history,PDFDocument
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: pdfreader -  How to browse PDF objects
   :og:description: Extracting raw data from PDF documents - direct objects access, accessing attributes,
       getting object by number and generation, browsing object history.
   :og:site_name: pdfreader docs
   :og:type: article


.. testsetup::

  import pkg_resources, os.path
  from pdfreader import PDFDocument
  samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  file_name = os.path.join(samples_dir, 'tutorial-example.pdf')


How to browse PDF objects
=========================

There could be a reason when you need to access raw PDF objects as they are in the document.
Or even get an object by its number and generation, which is also possible.
Let's see several examples with :class:`~pdfreader.document.PDFDocument`.

Accessing document objects
--------------------------

Let's take a sample file from :ref:`tutorial-document-catalog` tutorial.
We already discussed there how to locate document catalog.

.. doctest::

  >>> from pdfreader import PDFDocument
  >>> fd = open(file_name, "rb")
  >>> doc = PDFDocument(fd)
  >>> catalog = doc.root

To walk through the document you need to know object attributes and possible values.
It can be found on
`PDF-1.7 specification <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf>`_.
Then simply use attribute names in your python code.

.. doctest::

  >>> catalog.Type
  'Catalog'
  >>> catalog.Metadata.Type
  'Metadata'
  >>> catalog.Metadata.Subtype
  'XML'
  >>> pages_tree_root = catalog.Pages
  >>> pages_tree_root.Type
  'Pages'


Attribute names are cases sensitive. Missing or non-existing attributes have value of *None*

.. doctest::

  >>> catalog.type is None
  True
  >>> catalog.Metadata.subType is None
  True
  >>> catalog.Metadata.UnkNown_AttriBute is None
  True

If object is an array, access its items by index:

.. doctest::

  >>> first_page = pages_tree_root.Kids[0]
  >>> first_page.Type
  'Page'
  >>> first_page.Contents.Length
  3890

If object is a stream, you can get either raw data (deflated in this example):

.. doctest::

  >>> raw_data = first_page.Contents.stream
  >>> first_page.Contents.Length == len(raw_data)
  True
  >>> first_page.Contents.Filter
  'FlateDecode'

or decoded content:

.. doctest::

  >>> decoded_content = first_page.Contents.filtered
  >>> len(decoded_content)
  18428
  >>> decoded_content.startswith(b'BT\n0 0 0 rg\n/GS0 gs')
  True

All object reads are lazy. *pdfreader* reads an object when you access it for the first time.

Locate objects by number and generation
---------------------------------------

On the file structure level all objects have unique number an generation to identify them.
To get an object by number and generation
(for example to track object changes if incremental updates took place on file), just run:

.. doctest::

  >>> num, gen = 2, 0
  >>> raw_obj = doc.locate_object(num, gen)
  >>> obj = doc.build(raw_obj)
  >>> obj.Type
  'Catalog'

