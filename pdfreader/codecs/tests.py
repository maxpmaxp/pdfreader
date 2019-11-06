import unittest
import doctest

from . import codec


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(codec))
    return suite


def load_tests(loader, tests, ignore):
    tests.addTests(suite())
    return tests


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
