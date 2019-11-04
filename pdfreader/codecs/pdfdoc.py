import codecs

from typing import Tuple

PDFDocEncoding = "PDFDocEncoding"

encode_table = {'A': b'A', 'Æ': b'\xc6', 'Á': b'\xc1', 'Â': b'\xc2', 'Ä': b'\xc4', 'À': b'\xc0', 'Å': b'\xc5',
                'Ã': b'\xc3', 'B': b'B', 'C': b'C', 'Ç': b'\xc7', 'D': b'D', 'E': b'E', 'É': b'\xc9', 'Ê': b'\xca',
                'Ë': b'\xcb', 'È': b'\xc8', 'Ð': b'\xd0', '€': b'\xa0', 'F': b'F', 'G': b'G', 'H': b'H', 'I': b'I',
                'Í': b'\xcd', 'Î': b'\xce', 'Ï': b'\xcf', 'Ì': b'\xcc', 'J': b'J', 'K': b'K', 'L': b'L', 'Ł': b'\x95',
                'M': b'M', 'N': b'N', 'Ñ': b'\xd1', 'O': b'O', 'Œ': b'\x96', 'Ó': b'\xd3', 'Ô': b'\xd4', 'Ö': b'\xd6',
                'Ò': b'\xd2', 'Ø': b'\xd8', 'Õ': b'\xd5', 'P': b'P', 'Q': b'Q', 'R': b'R', 'S': b'S', 'Š': b'\x97',
                'T': b'T', 'Þ': b'\xde', 'U': b'U', 'Ú': b'\xda', 'Û': b'\xdb', 'Ü': b'\xdc', 'Ù': b'\xd9', 'V': b'V',
                'W': b'W', 'X': b'X', 'Y': b'Y', 'Ý': b'\xdd', 'Ÿ': b'\x98', 'Z': b'Z', 'Ž': b'\x99', 'a': b'a',
                'á': b'\xe1', 'â': b'\xe2', '´': b'\xb4', 'ä': b'\xe4', 'æ': b'\xe6', 'à': b'\xe0', '&': b'&',
                'å': b'\xe5', '^': b'^', '~': b'~', '*': b'*', '@': b'@', 'ã': b'\xe3', 'b': b'b', '\\': b'\\',
                '|': b'|', '{': b'{', '}': b'}', '[': b'[', ']': b']', '˘': b'\x18', '¦': b'\xa6', '•': b'\x80',
                'c': b'c', 'ˇ': b'\x19', 'ç': b'\xe7', '¸': b'\xb8', '¢': b'\xa2', 'ˆ': b'\x1a', ':': b':', ',': b',',
                '©': b'\xa9', '¤': b'\xa4', 'd': b'd', '†': b'\x81', '‡': b'\x82', '°': b'\x1e', '¨': b'\xa8',
                '÷': b'\xf7', '$': b'$', '˙': b'\x1b', 'ı': b'\x9a', 'e': b'e', 'é': b'\xe9', 'ê': b'\xea',
                'ë': b'\xeb', 'è': b'\xe8', '8': b'8', '…': b'\x83', '—': b'\x84', '–': b'\x85', '=': b'=',
                'ð': b'\xf0', '!': b'!', '¡': b'\xa1', 'f': b'f', 'ﬁ': b'\x93', '5': b'5', 'ﬂ': b'\x94',
                'ƒ': b'\x86', '4': b'4', '⁄': b'\x87', 'g': b'g', 'ß': b'\xdf', '`': b'`', '>': b'>', '«': b'\xab',
                '»': b'\xbb', '‹': b'\x88', '›': b'\x89', 'h': b'h', '˝': b'\x1c', '-': b'-', 'i': b'i', 'í': b'\xed',
                'î': b'\xee', 'ï': b'\xef', 'ì': b'\xec', 'j': b'j', 'k': b'k', 'l': b'l', '<': b'<', '¬': b'\xac',
                'ł': b'\x9b', 'm': b'm', '¯': b'\xaf', '−': b'\x8a', 'μ': b'\xb5', '×': b'\xd7', 'n': b'n', '9': b'9',
                'ñ': b'\xf1', '#': b'#', 'o': b'o', 'ó': b'\xf3', 'ô': b'\xf4', 'ö': b'\xf6', 'œ': b'\x9c',
                '˛': b'\x1d', 'ò': b'\xf2', '1': b'1', '½': b'\xbd', '¼': b'\xbc', '¹': b'\xb9', 'ª': b'\xaa',
                'º': b'\xba', 'ø': b'\xf8', 'õ': b'\xf5', 'p': b'p', '¶': b'\xb6', '(': b'(', ')': b')', '%': b'%',
                '.': b'.', '·': b'\xb7', '‰': b'\x8b', '+': b'+', '±': b'\xb1', 'q': b'q', '?': b'?', '¿': b'\xbf',
                '"': b'"', '„': b'\x8c', '“': b'\x8d', '”': b'\x8e', '‘': b'\x8f', '’': b'\x90', '‚': b'\x91',
                "'": b"'", 'r': b'r', '®': b'\xae', 's': b's', 'š': b'\x9d', '§': b'\xa7', ';': b';', '7': b'7',
                '6': b'6', '/': b'/', '\xa0': b' ', '£': b'\xa3', 't': b't', 'þ': b'\xfe', '3': b'3', '¾': b'\xbe',
                '³': b'\xb3', '˜': b'\x1f', '™': b'\x92', '2': b'2', '²': b'\xb2', 'u': b'u', 'ú': b'\xfa',
                'û': b'\xfb', 'ü': b'\xfc', 'ù': b'\xf9', '_': b'_', 'v': b'v', 'w': b'w', 'x': b'x', 'y': b'y',
                'ý': b'\xfd', 'ÿ': b'\xff', '¥': b'\xa5', 'z': b'z', 'ž': b'\x9e', '0': b'0'}

decode_table = {v[0]: k for k, v in encode_table.items()}


def encode(text: str) -> Tuple[bytes, int]:
    return b''.join(encode_table.get(x, x.encode("latin1", 'replace')) for x in text), len(text)


def decode(binary: bytes) -> Tuple[str, int]:
    return ''.join(decode_table.get(x, chr(x)) for x in binary), len(binary)


def search(encoding_name):
    return codecs.CodecInfo(encode, decode, name=PDFDocEncoding)


