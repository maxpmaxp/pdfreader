import unittest
import doctest

from . import base, cmap, document, inlineimage, content


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(base))
    suite.addTests(doctest.DocTestSuite(content))
    suite.addTests(doctest.DocTestSuite(cmap))
    suite.addTests(doctest.DocTestSuite(document))
    suite.addTests(doctest.DocTestSuite(inlineimage))
    return suite


def load_tests(loader, tests, ignore):
    tests.addTests(suite())
    return tests


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())