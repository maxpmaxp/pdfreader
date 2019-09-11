import unittest
import doctest

import pdfreader.buffer, pdfreader.document, pdfreader.parsers, pdfreader.types


def suite():
    suite = unittest.TestSuite()
    suite.addTests(doctest.DocTestSuite(pdfreader.buffer))
    suite.addTests(doctest.DocTestSuite(pdfreader.parsers.base))
    suite.addTests(doctest.DocTestSuite(pdfreader.parsers.document))
    suite.addTests(doctest.DocTestSuite(pdfreader.parsers.cmap))
    suite.addTests(doctest.DocTestSuite(pdfreader.types.cmap))
    suite.addTests(doctest.DocTestSuite(pdfreader.document))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())