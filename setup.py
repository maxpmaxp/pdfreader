#!/usr/bin/python
import sys

if sys.version_info[:2] < (3, 4):
    raise RuntimeError("Python version >= 3.4 required.")

import warnings

if sys.version_info[:2] < (3, 6):
    warnings.warn("Python version >= 3.6 required.")

version = '0.1.7'


import os.path

from setuptools import setup, find_packages
from distutils.cmd import Command


with open("README.rst") as f:
    try:
        readme_content = f.read()
    except:
        readme_content = ""


_HAVE_SPHINX = True
try:
    from sphinx.cmd import build as sphinx
except ImportError:
    try:
        import sphinx
    except ImportError:
        _HAVE_SPHINX = False


class doc(Command):

    description = "Generate or Test Documentation"

    user_options = [("test", "t",
                     "Run Doctests instead of generating documentation")]

    boolean_options = ["test"]

    def initialize_options(self):
        self.test = False

    def finalize_options(self):
        pass

    def run(self):

        if not _HAVE_SPHINX:
            raise RuntimeError(
                "You must install Sphinx to build or test the documentation.")

        if self.test:
            path = os.path.join(
                os.path.abspath('.'), "doc", "_build", "doctest")
            mode = "doctest"
        else:
            path = os.path.join(
                os.path.abspath('.'), "doc", "_build", version)
            mode = "html"

            try:
                os.makedirs(path)
            except:
                pass

        sphinx_args = ["-E", "-b", mode, "doc", path]

        if hasattr(sphinx, 'build_main'):
            status = sphinx.build_main(sphinx_args)
        else:
            status = sphinx.main(sphinx_args)

        if status:
            raise RuntimeError("documentation step '%s' failed" % (mode,))

        sys.stdout.write("\nDocumentation step '%s' performed, results here:\n"
                         "   %s/\n" % (mode, path))


class test(Command):
    description = "Run tests"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Installing required packages, running egg_info are
        # part of normal operation for setuptools.command.test.test
        if self.distribution.install_requires:
            self.distribution.fetch_build_eggs(
                self.distribution.install_requires)
        if self.distribution.tests_require:
            self.distribution.fetch_build_eggs(self.distribution.tests_require)
        self.run_command('egg_info')

        import unittest
        from pdfreader.tests import suite
        runner = unittest.TextTestRunner()
        result = runner.run(suite())
        sys.exit(not result.wasSuccessful())


setup(name="pdfreader",
      version=version,
      description="Pythonic API for parsing PDF files",
      long_description=readme_content,
      long_description_content_type='text/x-rst',
      author="Maksym Polshcha",
      author_email="maxp@sterch.net",
      maintainer="Maksym Polshcha",
      maintainer_email="maxp@sterch.net",
      url="http://github.com/maxpmaxp/pdfreader",
      keywords=["pdf", "pdfreader", "pdfparser", "adobe", "parser", "cmap"],
      license="MIT Licence",
      python_requires=">=3.4",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],

      packages=find_packages(exclude=["doc"]),
      package_data={'doc': ['doc/*']},
      zip_safe=False,
      install_requires=['bitarray>=1.1.0', 'pillow>=7.1.0', 'pycryptodome>=3.9.9'],
      entry_points={
        'console_scripts':
                [],
      },
      cmdclass={"doc": doc,
                "test": test}
  )
