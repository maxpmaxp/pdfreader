.. meta::
   :description: How to install pdfreader.
   :keywords: pdfreader,install,howto
   :google-site-verification: JxOmE0CjwDilnJCbNX5DOrH78HKS6snrAxA1SGvyAzs
   :og:title: How to install pdfreader
   :og:description: Instructions on how to install, upgrade build from sources pdfreader python package
   :og:site_name: pdfreader docs
   :og:type: article

Installing / Upgrading
======================
.. highlight:: bash

**pdfreader** is in the `Python Package Index
<http://pypi.python.org/pypi/pdfreader/>`_.


Installing with pip
-------------------
We recommend using `pip <http://pypi.python.org/pypi/pip>`_ to install *pdfreader* on all platforms::

  $ python -m pip install pdfreader

To get a specific version of pdfreader::

  $ python -m pip install pdfreader==0.1.2

To upgrade using pip::

  $ python -m pip install --upgrade pdfreader


Installing with easy_install
----------------------------

To install with ``easy_install`` from
`setuptools <http://pypi.python.org/pypi/setuptools>`_ do::

  $ python -m easy_install pdfreader


Installing from source
-----------------------

You can also download `the project source <http://github.com/maxpmaxp/pdfreader>`_ and do::

  $ git clone git://github.com/maxpmaxp/pdfreader.git pdfreader
  $ cd pdfreader/
  $ python setup.py install


Python versions support
-----------------------

*pdfreader* supports Python 3.6+. It might work on 3.4 and 3.5 but was never tested.

It is not compatible with Python 2.
