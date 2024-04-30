import logging
log = logging.getLogger(__name__)

from . import winansi, pdfdoc, macroman, standard
from .codec import Codec

known_base_codecs = (winansi.WinAnsiCodec, pdfdoc.PdfDocCodec, macroman.MacRomanCodec, standard.StandardCodec)
base_encodings_map = {c.name: c for c in known_base_codecs}

implicit_base_encoding = "StandardEncoding"


def DifferencesCodec(encoding_obj):
    """
        >>> from unittest.mock import Mock
        >>> obj = Mock()
        >>> obj.BaseEncoding = 'WinAnsiEncoding'
        >>> obj.Differences = [65, 'W', 'Y', 'Z']
        >>> obj.Type = 'Encoding'
        >>> codec = DifferencesCodec(obj)
        >>> codec.decode(b'ABC123DEF')
        ('WYZ123DEF', 9)


        >>> obj = Mock()
        >>> obj.BaseEncoding = 'WinAnsiEncoding'
        >>> obj.Differences = [65, 'a100', 'copyright', 'Aring']
        >>> obj.Type = 'Encoding'
        >>> codec = DifferencesCodec(obj)
        >>> codec.decode(b'ABC123DEF')
        ('❞©Å123DEF', 9)

        >>> obj = Mock()
        >>> obj.BaseEncoding = 'WinAnsiEncoding'
        >>> obj.Differences = None
        >>> obj.Type = 'Encoding'
        >>> codec = DifferencesCodec(obj)
        >>> codec.decode(b'ABC123DEF')
        ('ABC123DEF', 9)

    """

    try:
        enc = encoding_obj.BaseEncoding or implicit_base_encoding
        codec = base_encodings_map[enc]
    except KeyError:
        # There are usecases when BaseEncoding is None, Differences exists and all this makes sense as
        # content contains Differences characters only.
        # Anyway we have to try decode.
        log.debug("Unknown BaseEncoding {}. Trying {}".format(encoding_obj.BaseEncoding, implicit_base_encoding))
        codec = base_encodings_map[implicit_base_encoding]

    dt = dict(codec.decode_table)
    # update table with Differences
    if encoding_obj.Differences:
        for item in encoding_obj.Differences:
            if isinstance(item, int):
                # sequence start
                code = item
            else:
                dt[code] = item
                code += 1

    class CustomCodec(Codec):
        name = "{}-WithDifferences".format(codec.name)
        encode_table = codec.encode_table
        decode_table = dt
        use_ZapfDingbats = True

    return CustomCodec


if __name__ == "__main__":
    import doctest
    doctest.testmod()
