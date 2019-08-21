import re

from ..exceptions import TokenNotFound
from ..filestructure import Header
from .base import BaseParser


class HeaderParser(BaseParser):
    """
    1. Acrobat viewers require only that the header appear somewhere within the first 1024 bytes of the file
    2. Acrobat viewers will also accept a header in the form of
    %IPS-Adobe-N.n PDF-M.m

    >>> from io import BytesIO
    >>> f = BytesIO(b'%PDF-1.6\\nblablabla')
    >>> HeaderParser(f).parse()
    <PDF Header:v=b'1.6' (major=b'1, minor=6')>

    >>> f = BytesIO(b'%IPS-Adobe-1.3 PDF-1.6\\nblablabla')
    >>> HeaderParser(f).parse()
    <PDF Header:v=b'1.6' (major=b'1, minor=6')>

    >>> f = BytesIO(b'%some custom heading\\n%PDF-1.5\\nblablabla')
    >>> HeaderParser(f).parse()
    <PDF Header:v=b'1.5' (major=b'1, minor=5')>

    >>> f = BytesIO(b'%some custom heading\\n%IPS-Adobe-1.3 PDF-1.6\\nblablabla')
    >>> HeaderParser(f).parse()
    <PDF Header:v=b'1.6' (major=b'1, minor=6')>

    Test missing header and one out of 1024 leading bytes

    >>> f = BytesIO(b' '*1020 + b'\\n%PDF-1.5\\nblablabla')
    >>> HeaderParser(f).parse()
    Traceback (most recent call last):
    ...
    pdfreader.exceptions.TokenNotFound: No PDF header found


    >>> f = BytesIO(b'\\nblablabla'*100)
    >>> HeaderParser(f).parse()
    Traceback (most recent call last):
    ...
    pdfreader.exceptions.TokenNotFound: No PDF header found

    """

    HEADERS = (re.compile(b"%PDF-(\d\.\d)"), re.compile(b"%IPS-Adobe-\d\.\d PDF-(\d\.\d)"))

    def __init__(self, fileobj):
        super(HeaderParser, self).__init__(fileobj, 0)

    def parse(self):
        """ Parsers fileobj header and returns Header object """
        for r in self.HEADERS:
            m = r.search(self.data)
            if m:
                return Header(m.groups()[0], offset=m.start())
        raise TokenNotFound("No PDF header found")


if __name__ == "__main__":
    import doctest
    doctest.testmod()