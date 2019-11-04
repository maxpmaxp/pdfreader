from . import winansi, pdfdoc, macroman, standard
from .codec import Codec

known_base_codecs = (winansi.WinAnsiCodec, pdfdoc.PdfDocCodec, macroman.MacRomanCodec, standard.StandardCodec)
base_encodings_map = {c.name: c for c in known_base_codecs}


def DifferencesCodec(encoding_obj):
    # {'BaseEncoding': 'WinAnsiEncoding',
    #  'Differences': [1, 'S', 'u', 'm', 'o', 'n', 's', 'space', 'P', 'a', 'g', 'e', 'f', 'l', 'i', 't', 'quoteright', 'C', 'p'],
    # 'Type': 'Encoding'}
    try:
        codec = base_encodings_map[encoding_obj.BaseEncoding]
    except KeyError:
        raise LookupError("Unknown BaseEncoding {}".format(encoding_obj.BaseEncoding))

    dt = dict(codec.decode_table)
    # update table with Differences
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

    return CustomCodec
