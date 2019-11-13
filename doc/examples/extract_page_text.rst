How to parse PDF texts
======================

Simple ways of getting plain texts and formatted texts from documents are discussed in the tutorial :ref:`tutorial-texts`,
so let's focus on advanced techniques.

In this example we build a parser for :download:`traffic crash reports <pdfs/example-text-crash-report.pdf>`,
that extracts:

 - local report number
 - reporting agency name
 - crash severity

from the first page. The parser can be applied to all crash reports like that.

.. image:: img/example-text-crash-report.png

Let's open the document and get the first page:

.. doctest::

  >>> from pdfreader import PDFDocument
  >>> import pkg_resources, os.path
  >>> samples_dir = pkg_resources.resource_filename('doc', 'examples/pdfs')
  >>> file_name = os.path.join(samples_dir, 'example-text-crash-report.pdf')
  >>> fd = open(file_name, "rb")
  >>> doc = PDFDocument(fd)
  >>> page = next(doc.pages())


Introduction to text objects
----------------------------

Every PDF page has one or more binary content streams associated with it. Streams may contain inline images,
text blocks, text formatting instructions, display device commands etc. In this example we stay focused on text blocks.

Every text block in a stream is surrounded by BT/ET instructions
and represented as :class:`~pdfreader.types.content.TextObject` instance.
Typically a single page has one or more text blocks.

:meth:`~pdfreader.types.obects.Page.text_objects` is a generator yielding all
:class:`~pdfreader.types.content.TextObject` instances for a page.


How text objects work
---------------------

Let's have a look at the first text object on the page.

.. doctest::

  >>> tobj = next(page.text_objects())
  >>> tobj.source
  'BT /F3 6.0 Tf 0 0 0 rg 314.172 TL 168.624 759.384 Td (LOCAL INFORMATION) Tj T* ET'

This text block contains instructions for a viewer (font, positioning etc.) and one string surrounded by brackets.

.. doctest::

  >>> tobj.strings
  ['LOCAL INFORMATION']

:class:`~pdfreader.types.content.TextObject` attributes are:

- :attr:`~pdfreader.types.content.TextObject.source` - contains all data within a single BT/ET block:
  commands and text strings. All text strings are surrounded by brackets and decoded
  according to the used font settings (`Tf` command).
  The value can be used to parse text content by PDF markdown.

- :attr:`~pdfreader.types.content.TextObject.strings` - list of all strings within the text block. No PDF markdown here.


Method :meth:`~pdfreader.types.content.TextObject.to_string` is just a syntax sugar to join `TextObject.strings` using
some glue characters.

.. doctest::

  >>> tobj.to_string()
  'LOCAL INFORMATION'

Let's extract all text objects from the page. This can be done either by getting all text objects
and joining the sources

.. doctest::

  >>> all_sources = [to.source for to in page.text_objects()]
  >>> markdown_from_tobjs = "\n".join(all_sources)

or by calling :meth:`~pdfreader.types.obects.Page.text_sources`, which is a syntax sugar for the above.

.. doctest::

  >>> markdown = page.text_sources()
  >>> markdown == markdown_from_tobjs
  True


How to parse PDF markdown
-------------------------

At this point a string variable `markdown` contains all texts with PDF markdown from the page.

.. doctest::

  >>> isinstance(markdown, str)
  True

Let's save it as a text file and analyze how can we extract the data we need.

.. doctest::

  >>> with open("example-crash-markdown.txt", "w") as f:
  ...     f.write(markdown)
  26700

Open your favorite editor and have a look at :download:`the file <downloads/example-crash-markdown.txt>`.

Now we may use any text processing tools like regular expressions, grep, custom parsers to extract the data.

.. doctest::

  >>> reporting_agency = markdown.split('(REPORTING AGENCY NAME *)', 1)[1].split('(', 1)[1].split(')',1)[0]
  >>> reporting_agency
  'Ohio State Highway Patrol'

  >>> local_report_number = markdown.split('(LOCAL REPORT NUMBER *)', 1)[1].split('(', 1)[1].split(')',1)[0]
  >>> local_report_number
  '02-0005-02'

  >>> crash_severity = markdown.split('( ERROR)', 1)[1].split('(', 1)[1].split(')',1)[0]
  >>> crash_severity
  '1'

Here we are!


More ways to extract texts
--------------------------

There are more ways to extract texts from documents.

:meth:`~pdfreader.types.obects.Page.texts` - returns all page strings as a plain text

.. doctest::

  >>> page_plain_text = page.text()

:meth:`~pdfreader.document.PDFDocument.text_sources` - returns all document texts with markdown.

.. doctest::

  >>> doc_text_markdown = doc.text_sources()

:meth:`~pdfreader.document.PDFDocument.text_objects` - yields all document text objects page by page.

.. doctest::

  >>> tobj_generator = doc.text_objects()
  >>> first_obj = next(tobj_generator)


Useful links
------------

Detailed description of PDF texts is
`here (see sec. 9) <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf#page=237>`_
