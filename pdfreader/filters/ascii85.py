import logging
log = logging.getLogger(__name__)

from base64 import  a85decode

from ..constants import WHITESPACES

filter_names = ('ASCII85Decode', 'A85')


def decode(data, *_):
    """
    >>> from base64 import a85encode
    >>> data = a85encode(b'sample data') + b'~>'
    >>> decode(data)
    b'sample data'

    >>> data = b"BROKEN_STREAM"
    >>> decode(data)
    b''
    """
    # filter whitespaces
    ws = b''.join(WHITESPACES)
    data = bytes([n for n in data if n not in ws])
    try:
        if data.endswith(b'~>'):
            res = a85decode(data[:-2])
        else:
            raise ValueError("EOD ~> expected")
    except (TypeError, ValueError):
        log.exception("Skipping broken stream")
        res = b''
    return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
