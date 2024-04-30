import re

from dateutil import tz
from dateutil.parser import parse as parse_date, parserinfo

from .constants import ESCAPED_CHARS


RE_PDF_DATETIME = re.compile("^D:(\d\d\d\d)(\d\d)(\d\d)(\d\d)(\d\d)(\d\d)([+\-Zz])(\d\d)'(\d\d)'$")


class cached_property(object):
    """ A property that is only computed once per instance and then replaces
        itself with an ordinary attribute. Deleting the attribute resets the
        property. """

    def __init__(self, func):
        self.__doc__ = func.__doc__
        self.func = func

    def __get__(self, obj, cls):
        if obj is None: return self
        value = obj.__dict__[self.func.__name__] = self.func(obj)
        return value


def pdf_escape_string(s: str):
    res = ""
    for c in s:
        res += ESCAPED_CHARS.get(c, c)
    return res


def from_pdf_datetime(s):
    """ Parses PDF datetime into pythonixc datetime

    :param s: string in PDF datetime format D:YYYYMMDDHHmmSSOHH'mm'
    :return: datetime

    >>> from_pdf_datetime("D:20210212014204Z00'00'")
    datetime.datetime(2021, 2, 12, 1, 42, 4, tzinfo=tzutc())

    >>> from_pdf_datetime("D:20210212014204+01'00'")
    datetime.datetime(2021, 2, 12, 1, 42, 4, tzinfo=tzoffset(None, 3600))

    >>> from_pdf_datetime("D:20210212014204-01'00'")
    datetime.datetime(2021, 2, 12, 1, 42, 4, tzinfo=tzoffset(None, -3600))

    >>> from_pdf_datetime("D:20210212014204?01'00'")
    Traceback (most recent call last):
    ...
    ValueError: Incorrect pdf time value D:20210212014204?01'00'. Expected D:YYYYMMDDHHmmSSOHH'mm'

    >>> from_pdf_datetime("blablabla")
    Traceback (most recent call last):
    ...
    ValueError: Incorrect pdf time value blablabla. Expected D:YYYYMMDDHHmmSSOHH'mm'

    """
    if not RE_PDF_DATETIME.match(s):
        raise ValueError("Incorrect pdf time value {}. Expected D:YYYYMMDDHHmmSSOHH'mm'".format(s))
    tzinfos = {x: tz.tzutc() for x in parserinfo().UTCZONE}

    iso6801 = RE_PDF_DATETIME.sub(r"\1-\2-\3T\4:\5:\6\7\8:\9", s).replace("Z", "+")
    return parse_date(iso6801, tzinfos=tzinfos)
