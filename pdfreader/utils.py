
from .constants import ESCAPED_CHARS

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
