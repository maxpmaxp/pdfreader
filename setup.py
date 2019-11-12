#!/usr/bin/python
from os.path import isfile
import os

import setuptools
from setuptools import setup, find_packages

from distutils.version import LooseVersion
import warnings

if isfile("MANIFEST"):
    os.unlink("MANIFEST")

if LooseVersion(setuptools.__version__) <= LooseVersion("24.3"):
    warnings.warn("python_requires requires setuptools version > 24.3",
                  UserWarning)


with open("README.rst") as f:
    try:
        readme_content = f.read()
    except:
        readme_content = ""


setup(name="pdfreader",
      version='0.1.2',
      description="Pythonic API for parsing PDF files",
      long_description=readme_content,
      author="Maksym Polshcha",
      author_email="maxp@sterch.net",
      maintainer="Maksym Polshcha",
      maintainer_email="maxp@sterch.net",
      url="http://github.com/maxpmaxp/pdfreader",
      keywords=["pdf", "pdfreader", "pdfparser", "adobe", "parser", "portable document format", "cmap"],
      install_requires=[],
      license="MIT Licence",
      python_requires=">=3.4",
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
      ],

      packages=find_packages(exclude=["samples"]),
      package_dir={'pdfreader': 'pdfreader'},
      package_data={'samples': ['samples/*']},
      zip_safe=False,
      requires=['bitarray>=1.1.0', 'pillow>=6.2.0'],
      entry_points={
        'console_scripts':
                [],
      })