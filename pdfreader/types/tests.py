import unittest
import doctest

from . import cmap


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(cmap))
    return suite


def load_tests(loader, tests, ignore):
    tests.addTests(suite())
    return tests


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())