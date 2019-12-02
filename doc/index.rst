.. meta::
   :description: pdfreader - Python API to parse PDF documents, extract texts, images, other objects.
   :keywords: pdf,python,pdfreader,parse,parser,acrobat,extract,text,image,xobject,cmap.
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: pdfreader - Python API for PDF
   :og:url: http://pdfreader.readthedocs.io/
   :og:description: Pythonic API to parse PDF documents, extract texts (plain and formatted), images, other objects.
   :og:site_name: pdfreader docs
   :og:type: website

pdfreader |release| Documentation
=================================

Overview
--------
**pdfreader** is a Pythonic API to PDF documents which follows
`PDF-1.7 specification <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf>`_.

It allows to parse documents, extract texts, images, fonts,
`CMaps <https://www.adobe.com/content/dam/acom/en/devnet/font/pdfs/5014.CIDFont_Spec.pdf>`_, and other data;
access different objects within PDF documents.

Features:

* Extracts texts (plain and formatted)
* Extracts forms data (plain and formatted)
* Extracts images and image masks as `Pillow/PIL Images <https://pillow.readthedocs.io/en/stable/reference/Image.html>`_
* Supports all PDF encodings, CMap, predefined cmaps.
* Browse any document objects, resources and extract any data you need (fonts, annotations, metadata, multimedia, etc.)
* Document history access and access to previous document versions if incremental updates are in place.
* Follows `PDF-1.7 specification <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf>`_
* Fast document processing due to lazy objects access


:doc:`installation`
  Instructions on how to get and install the distribution.

:doc:`tutorial`
  A quick overview on how to start.

:doc:`examples/index`
  Examples of how to perform specific tasks.

:doc:`api/index`
  API documentation, organized by module.


Issues, Support and Feature Requests
------------------------------------
If you're having trouble, have questions about *pdfreader*, or need some features the best place to ask
is the `Github issue tracker <https://github.com/maxpmaxp/pdfreader/issues>`_.
Once you get an answer, it'd be great if you could work it back into this documentation and contribute!


Contributing
------------
*pdfreader* is an open source project. You're welcome to contribute:

* Code patches
* Bug reports
* Patch reviews
* Introduce new features
* Documentation improvements

*pdfreader* uses GitHub `issues <https://github.com/maxpmaxp/pdfreader/issues>`_ to keep track of bugs,
feature requests, etc.

See `project sources <https://github.com/maxpmaxp/pdfreader>`_

Donation
--------
If this project is helpful, you can treat me to coffee :-)

.. image:: https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif
   :target: https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=VMVFZSDHDFVK6&item_name=PDFReader+support&currency_code=USD&source=url


About This Documentation
------------------------
This documentation is generated using the `Sphinx
<http://sphinx.pocoo.org/>`_ documentation generator. The source files
for the documentation are located in the *doc/* directory of the
*pdfreader* distribution. To generate the docs locally run the
following command from the root directory of the *pdfreader* source:

.. code-block:: bash

  $ python setup.py doc


Table of Contents
-----------------


.. toctree::
   :maxdepth: 3

   installation
   tutorial
   examples/index
   api/index
