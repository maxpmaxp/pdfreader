import unittest
import doctest

from . import codec, differences, decoder


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(codec))
    suite.addTests(doctest.DocTestSuite(differences))
    suite.addTests(doctest.DocTestSuite(decoder))
    return suite


def load_tests(loader, tests, ignore):
    tests.addTests(suite())
    return tests


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())
