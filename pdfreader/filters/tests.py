import unittest
import doctest

from . import decoders


def suite():
    loader = unittest.TestLoader()
    suite = loader.discover('.', 'test_*')
    for m in decoders:
        suite.addTests(doctest.DocTestSuite(m))
    return suite


def load_tests(loader, tests, ignore):
    tests.addTests(suite())
    return tests


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
