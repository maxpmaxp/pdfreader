import codecs

from collections import defaultdict

from typing import Tuple

from .agl import AGL
from .zapfdingbatsgl import ZAPFDINGBATS_GL


_cache = defaultdict(dict)


class Codec(object):

    encode_table = NotImplemented
    decode_table = NotImplemented
    name = NotImplemented
    use_ZapfDingbats = False

    @classmethod
    def glyph_name_to_string(cls, name):
        """
            See https://github.com/adobe-type-tools/agl-specification

            >>> from pdfreader.codecs.codec import Codec
            >>> Codec.glyph_name_to_string("Lcommaaccent") == "\\u013B"
            True
            >>> Codec.glyph_name_to_string("uni20AC0308") == "\\u20AC\\u0308"
            True
            >>> Codec.glyph_name_to_string("u1040C") == "\\U0001040C"
            True
            >>> Codec.glyph_name_to_string("uni20ac") == "\\u20AC"
            True
            >>> Codec.glyph_name_to_string("Lcommaaccent_uni20AC0308_u1040C.alternate") == "\\u013B\\u20AC\\u0308\\U0001040C"
            True
            >>> Codec.glyph_name_to_string("Lcommaaccent_uni20AC0308_u1040C.alternate") == "\\u013B\\u20AC\\u0308\\U0001040C"
            True
            >>> Codec.glyph_name_to_string("UnKnowN")
            ''
            >>> Codec.glyph_name_to_string("UnKnowN_uni20ac") == "\\u20AC"
            True
            >>> Codec.glyph_name_to_string("uni0UNK")
            ''
            >>> Codec.glyph_name_to_string("uUNKN")
            ''
            >>> Codec.glyph_name_to_string("uni01")
            ''
            >>> Codec.glyph_name_to_string("u01")
            ''
            >>> Codec.glyph_name_to_string("u1234567")
            ''
            >>> Codec.glyph_name_to_string("uni1234567")
            ''
            >>> Codec.glyph_name_to_string("uni1234567_uni20ac") == "\\u20AC"
            True
            >>> Codec.glyph_name_to_string("uni1234567_uni20ac") == "\\u20AC"
            True
            >>> Codec.glyph_name_to_string("UnKnowN_uni20ac.alternate") == "\\u20AC"
            True
            >>> Codec.glyph_name_to_string("a100")
            ''
        """
        if name in _cache[cls]:
            return _cache[cls][name]

        components = name.split(".")[0].split("_")
        res = ""

        for glyph in components:
            val = ""
            if cls.use_ZapfDingbats and glyph in ZAPFDINGBATS_GL:
                val = ZAPFDINGBATS_GL[glyph]
            elif glyph in AGL:
                val = AGL[glyph]
            elif glyph.startswith("uni") and (len(glyph) - 3) % 4 == 0:
                try:
                    val = "".join([chr(int(glyph[i:i+4], 16)) for i in range(3, len(glyph), 4)])
                except ValueError:
                    # char code out of range
                    pass
            elif glyph.startswith("u") and 5 <= len(glyph) <= 7:
                try:
                    val = chr(int(glyph[1:], 16))
                except ValueError:
                    # char code out of range
                    pass
            res += val

        _cache[cls][name] = res
        return res

    @classmethod
    def encode(cls, text: str) -> Tuple[bytes, int]:
        return b''.join(cls.encode_table.get(x, x.encode("latin1", 'replace')) for x in text), len(text)

    @classmethod
    def decode(cls, binary: bytes) -> Tuple[str, int]:
        res = ''
        for x in binary:
            if x in cls.decode_table:
                glyph_name = cls.decode_table[x]
                glyph = cls.glyph_name_to_string(glyph_name)
            else:
                # treat unlisted codes as unicode characters
                glyph = chr(x)
            res += glyph
        return res, len(binary)

    @classmethod
    def search(cls, encoding_name):
        return codecs.CodecInfo(cls.encode, cls.decode, name=cls.name)


class ZapfDingbatsCodec(Codec):
    """
        Supports ZapfDingbats symbol names

        See See https://github.com/adobe-type-tools/agl-specification

        >>> ZapfDingbatsCodec.glyph_name_to_string("a100") == '\\u275E'
        True
        >>> ZapfDingbatsCodec.glyph_name_to_string("a100_Lcommaaccent") == '\\u275E\\u013B'
        True
        >>> ZapfDingbatsCodec.glyph_name_to_string("a100_u013B") == '\\u275E\\u013B'
        True
        >>> ZapfDingbatsCodec.glyph_name_to_string("a100_uni013B") == '\\u275E\\u013B'
        True
        >>> ZapfDingbatsCodec.glyph_name_to_string("a100_uni013B.alternate") == '\\u275E\\u013B'
        True
    """
    use_ZapfDingbats = True


if __name__ == "__main__":
    import doctest
    doctest.testmod()
