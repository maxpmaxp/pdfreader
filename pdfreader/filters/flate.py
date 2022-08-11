import zlib
import logging
log = logging.getLogger(__name__)

from .predictors import _remove_predictors

filter_names = ('FlateDecode', 'Fl')


def decode(data, params):
    """
    >>> from zlib import compress
    >>> data = compress(b'sample data')
    >>> decode(data, dict(Predictor=1))
    b'sample data'

    >>> data = b"BROKEN_STREAM"
    >>> decode(data, dict(Predictor=1))
    b''
    """
    try:
        data = zlib.decompress(data)
        data = _remove_predictors(data, params.get("Predictor"), params.get("Columns"))
    except zlib.error:
        log.exception("Skipping broken stream")
        data = b''
    return data


if __name__ == "__main__":
    import doctest
    doctest.testmod()
