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


setup(name="pdfreader",
      version='0.1.1dev3',
      description="PDF reader",
      author="Maksym Polshcha",
      author_email="maxp@sterch.net",
      maintainer="Maksym Polshcha",
      maintainer_email="maxp@sterch.net",
      packages=find_packages(exclude=["samples"]),
      package_dir={'pdfreader': 'pdfreader'},
      package_data={'samples': ['samples/*']},
      zip_safe=False,
      requires=['pillow'],
      entry_points={
        'console_scripts':
                [],
      })