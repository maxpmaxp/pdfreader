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

* Follows `PDF-1.7 specification <https://www.adobe.com/content/dam/acom/en/devnet/pdf/pdfs/PDF32000_2008.pdf>`_
* Lazy objects access allows to process huge PDF documents quite fast
* Allows to extract texts (pure strings and formatted text objects)
* Allows to extract PDF forms data (pure strings and formatted text objects)
* Supports all PDF encodings, CMap, predefined cmaps.
* Allows to extract images and image masks as `Pillow/PIL Images <https://pillow.readthedocs.io/en/stable/reference/Image.html>`_ without loosing any quality
* Allows to access any document objects, resources and extract any data you need (fonts, annotations, metadata, multimedia, etc.)

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


About This Documentation
------------------------
This documentation is generated using the `Sphinx
<http://sphinx.pocoo.org/>`_ documentation generator. The source files
for the documentation are located in the *doc/* directory of the
**pdfreader** distribution. To generate the docs locally run the
following command from the root directory of the **pdfreader** source:

.. code-block:: bash

  $ python setup.py doc

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

.. toctree::
   :hidden:

   installation
   tutorial
   examples/index
   api/index
