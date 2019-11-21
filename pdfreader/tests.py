import unittest
import doctest

import pdfreader.buffer, pdfreader.document


def suite():
    loader = unittest.TestLoader()
    suite = loader.discover('.')
    suite.addTests(doctest.DocTestSuite(pdfreader.buffer))
    return suite


if __name__ == '__main__':
    runner = unittest.TextTestRunner()
    runner.run(suite())