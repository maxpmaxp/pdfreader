from itertools import product, chain

from . import ascii85, asciihex, flate, lzw, runlength, ccittfax,  dct, jbig2, jpx, crypt

decoders = (ascii85, asciihex, flate, lzw, runlength, ccittfax, dct, jbig2, jpx, crypt)

decoders_by_name = dict(chain.from_iterable(list(product(m.filter_names, [m])) for m in decoders))


def apply_filter(name, binary, params=None):
    decoder = decoders_by_name.get(name)
    if decoder is None:
        raise NotImplementedError(decoder)
    return decoder.decode(binary, params or {})

# Not implemented:
# - dct
# - jbig2
# - jpx
# - crypt
