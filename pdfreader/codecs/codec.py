import codecs

from typing import Tuple

from .agl import AGL


class Codec(object):

    encode_table = NotImplemented
    decode_table = NotImplemented
    name = NotImplemented

    @classmethod
    def encode(cls, text: str) -> Tuple[bytes, int]:
        return b''.join(cls.encode_table.get(x, x.encode("latin1", 'replace')) for x in text), len(text)

    @classmethod
    def decode(cls, binary: bytes) -> Tuple[str, int]:
        res = ''
        for x in binary:
            if x in cls.decode_table:
                glyph_name = cls.decode_table[x]
                glyph = AGL.get(glyph_name, glyph_name) # Leave unknown glyph names as is
            else:
                # treat unlisted codes as unicode characters
                glyph = chr(x)
            res += glyph
        return res, len(binary)

    @classmethod
    def search(cls, encoding_name):
        return codecs.CodecInfo(cls.encode, cls.decode, name=cls.name)
