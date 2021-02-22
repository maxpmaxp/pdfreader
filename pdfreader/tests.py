import unittest
import doctest

import pdfreader.buffer, pdfreader.document, pdfreader.utils


def suite():
    loader = unittest.TestLoader()
    suite = loader.discover('.')
    suite.addTests(doctest.DocTestSuite(pdfreader.buffer))
    suite.addTests(doctest.DocTestSuite(pdfreader.document))
    suite.addTests(doctest.DocTestSuite(pdfreader.utils))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())