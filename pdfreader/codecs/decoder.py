import codecs
import logging

from ..constants import DEFAULT_ENCODING
from ..types.native import HexString
from . import register_pdf_encodings

register_pdf_encodings()


class BaseDecoder(object):
    def __init__(self, font):
        self.cmap = font.get("ToUnicode")
        self.encoding = font.get('Encoding')

    def decode_string(self, s):
        s_hex = HexString("".join(hex(b)[2:].zfill(2) for b in s))
        return self.decode_hexstring(s_hex)

    def decode_hexstring(self, s: HexString):
        raise NotImplementedError()


class CMAPDecoder(BaseDecoder):

    def decode_hexstring(self, s: HexString):
        res, code = "", ""

        for i in range(0, len(s), 2):
            code += s[i:i + 2]
            try:
                ch = self.cmap.resource.bf_ranges[code]
            except KeyError:
                if len(code) < 4:
                    continue
                else:
                    # leave as is
                    ch = HexString(code).to_string()
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
        # ToDo: Differences support. See p263 PDF32000_2008.pdf
        try:
            codec = codecs.lookup(self.encoding)
        except LookupError:
            logging.warning("Unsupported encoding {}. Using default {}".format(self.encoding, DEFAULT_ENCODING))
            codec = codecs.lookup(DEFAULT_ENCODING)

        return codec.decode(s)[0]


default_decoder = EncodingDecoder(dict(Encoding="latin1"))


def Decoder(font):
    klass = CMAPDecoder if font.get("ToUnicode") else EncodingDecoder
    return klass(font)
