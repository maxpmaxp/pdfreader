import codecs
import logging
import pkg_resources

from io import BytesIO

from ..codecs.differences import DifferencesCodec
from ..constants import DEFAULT_ENCODING, predefined_cmap_names
from ..parsers.cmap import CMapParser
from ..types.native import HexString, Name
from . import register_pdf_encodings

register_pdf_encodings()


class PredefinedCmaps(object):
    _cache = dict()

    @staticmethod
    def _load(name):
        from ..parsers import CMapParser
        fname = predefined_cmap_names[name]
        with pkg_resources.resource_stream('pdfreader.codecs', 'cmaps/{}'.format(fname)) as fd:
            return CMapParser(fd).cmap()

    @staticmethod
    def get(name):
        if name not in PredefinedCmaps._cache:
            PredefinedCmaps._cache[name] = PredefinedCmaps._load(name)
        return PredefinedCmaps._cache[name]


def _guess_encoding_by_font_name(name):
    """ Try to guess encoding from font name if it is one of 14 PostScript predefined or some other
        PDF can recognize.
    """
    encoding = None
    if name == 'Symbol':
        # ToDo: It must be cp1038 decoder, which is missing now. it's one of predefined PostScript fonts
        logging.warning("Symbol (aka cp1038) codec not implemented")
        encoding = 'Identity-H'
    elif name in ('Times-Roman', 'Helvetica', 'Courier', 'Symbol', 'Times-Bold', 'Helvetica-Bold', 'Courier-Bold',
                  'Times-Italic', 'Helvetica-Qblique', 'Courier-Oblique', 'Times-BoldItalic', 'Helvetica-BoldOblique',
                  'Courier-BoldOblique', 'ZapfDingbats'):
        # Predefined PostScript fonts
        encoding = 'Identity-H'
    return encoding


def _get_cmap_encoding(font):
    cmap = encoding = None
    explicit_cmap = font.get("ToUnicode")
    explicit_encoding = font.get('Encoding')
    is_predefined_cmap = isinstance(explicit_encoding, Name) and explicit_encoding in predefined_cmap_names
    if bool(explicit_cmap):
        cmap = CMapParser(BytesIO(explicit_cmap.filtered)).cmap()
    elif is_predefined_cmap:
        # Get predefined cmap by name
        cmap = PredefinedCmaps.get(explicit_encoding)

    if not is_predefined_cmap:
        encoding = explicit_encoding

    if cmap is None and encoding is None:
        encoding = _guess_encoding_by_font_name(font.get('BaseFont'))

    return cmap, encoding


class BaseDecoder(object):
    def __init__(self, font):
        self.cmap, self.encoding = _get_cmap_encoding(font)

    def decode_string(self, s):
        raise NotImplementedError()

    def decode_hexstring(self, s: HexString):
        raise NotImplementedError()


class CMAPDecoder(BaseDecoder):
    """

    >>> font = dict(Encoding=Name("Identity-V"))
    >>> decoder = CMAPDecoder(font)
    >>> decoder.decode_hexstring('004100420043003100320033')
    'ABC123'

    >>> font = dict(Encoding=Name("83pv-RKSJ-H"))
    >>> decoder = CMAPDecoder(font)
    >>> decoder.decode_hexstring('82A88D7B0057') == "\\u82A8\\u8D7BW"
    True

    >>> from unittest.mock import Mock, patch
    >>> import pdfreader.codecs.decoder
    >>> cmap = Mock()
    >>> cmap.bf_ranges = {'0001': 'A', '0002': 'B', '0003': 'C', '0004': '1',  '0005': '2',  '0006': '3'}
    >>> with patch.object(pdfreader.codecs.decoder, '_get_cmap_encoding', return_value=(cmap, None)) as _:
    ...     decoder = CMAPDecoder(Mock())
    ...     decoder.decode_hexstring('000100020003000400050006')
    'ABC123'

    """

    def decode_hexstring(self, s: HexString):
        res, code = "", ""
        for i in range(0, len(s), 2):
            code += s[i:i + 2]
            try:
                ch = self.cmap.bf_ranges[code]
            except KeyError:
                if len(code) < 4:
                    continue
                else:
                    # leave as is
                    try:
                        ch = chr(int(code, 16))
                    except ValueError:
                        ch = HexString(code)
            res += ch
            code = ""

        if code:
            hs = HexString(code)
            res += hs.to_bytes().decode(self.encoding) if self.encoding else hs.to_string()

        return res

    def decode_string(self, s):
        s_hex = HexString(s.hex().upper())
        return self.decode_hexstring(s_hex)


class EncodingDecoder(BaseDecoder):

    def decode_hexstring(self, s: HexString):
        return self.decode_string(s.to_bytes())

    def decode_string(self, s):
        from ..types.objects import Encoding

        if isinstance(self.encoding, str):
            # encoding name
            try:
                codec = codecs.lookup(self.encoding)
            except LookupError:
                logging.warning("Unsupported encoding {}. Using default {}".format(self.encoding, DEFAULT_ENCODING))
                codec = codecs.lookup(DEFAULT_ENCODING)
        elif isinstance(self.encoding, Encoding):
            # Encoding object - See PDF spec PDF32000_2008.pdf p.255 sec 9.6.1
            # Base encoding with differences
            codec = DifferencesCodec(self.encoding)
        else:
            # This should never happen
            raise TypeError("Unexpected type. Probably a bug: {} type of {}".format(self.encoding, type(self.encoding)))
        return codec.decode(s)[0]


default_decoder = EncodingDecoder(dict(Encoding="latin1"))


def Decoder(font):
    cmap, encoding = _get_cmap_encoding(font)
    if cmap:
        decoder = CMAPDecoder(font)
    elif encoding:
        decoder = EncodingDecoder(font)
    else:
        # Encoding can be defined as a part of PostScript Font program, which is not supported.
        # Anyway, let's try do decode somehow.
        logging.warning("Can't build Decoder for font {}. Trying to use default.".format(font))
        decoder = default_decoder
    return decoder


if __name__ == "__main__":
    import doctest
    doctest.testmod()
