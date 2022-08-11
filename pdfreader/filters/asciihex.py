import logging
log = logging.getLogger(__name__)

from ..constants import WHITESPACES, DEFAULT_ENCODING


filter_names = ('ASCIIHexDecode', 'AHx')


def decode(data, *_):
    """
    >>> data = b"646174612073616d706c65>"
    >>> decode(data)
    b'data sample'

    >>> data = b"64617461207 3616d\\n706c65>"
    >>> decode(data)
    b'data sample'

    >>> data = b"64617461207 3616d\\n706c652>"
    >>> decode(data)
    b'data sample '

    >>> data = b"BROKEN_STREAM>"
    >>> decode(data)
    b''
    """
    buffer = b""
    res = b""
    try:
        for i in range(0, len(data)):
            c = data[i:i + 1]
            if c in WHITESPACES:
                continue
            elif c == b">":
                break
            buffer += c
            if len(buffer) > 1:
                res += bytes.fromhex(buffer.decode(DEFAULT_ENCODING))
                buffer = b""

        if buffer:
            if len(buffer) == 1:
                buffer += b"0"
            res += bytes.fromhex(buffer.decode(DEFAULT_ENCODING))
    except ValueError:
        # invalid characters on stream
        log.exception("Skipping broken stream")
    return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
