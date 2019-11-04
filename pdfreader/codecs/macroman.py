import codecs

from typing import Tuple

MacRomanEncoding = "MacRomanEncoding"

encode_table = {'A': b'A', 'Æ': b'\xae', 'Á': b'\xe7', 'Â': b'\xe5', 'Ä': b'\x80', 'À': b'\xcb', 'Å': b'\x81',
                'Ã': b'\xcc', 'B': b'B', 'C': b'C', 'Ç': b'\x82', 'D': b'D', 'E': b'E', 'É': b'\x83', 'Ê': b'\xe6',
                'Ë': b'\xe8', 'È': b'\xe9', 'F': b'F', 'G': b'G', 'H': b'H', 'I': b'I', 'Í': b'\xea', 'Î': b'\xeb',
                'Ï': b'\xec', 'Ì': b'\xed', 'J': b'J', 'K': b'K', 'L': b'L', 'M': b'M', 'N': b'N', 'Ñ': b'\x84',
                'O': b'O', 'Œ': b'\xce', 'Ó': b'\xee', 'Ô': b'\xef', 'Ö': b'\x85', 'Ò': b'\xf1', 'Ø': b'\xaf',
                'Õ': b'\xcd', 'P': b'P', 'Q': b'Q', 'R': b'R', 'S': b'S', 'T': b'T', 'U': b'U', 'Ú': b'\xf2',
                'Û': b'\xf3', 'Ü': b'\x86', 'Ù': b'\xf4', 'V': b'V', 'W': b'W', 'X': b'X', 'Y': b'Y', 'Ÿ': b'\xd9',
                'Z': b'Z', 'a': b'a', 'á': b'\x87', 'â': b'\x89', '´': b'\xab', 'ä': b'\x8a', 'æ': b'\xbe',
                'à': b'\x88', '&': b'&', 'å': b'\x8c', '^': b'^', '~': b'~', '*': b'*', '@': b'@', 'ã': b'\x8b',
                'b': b'b', '\\': b'\\', '|': b'|', '{': b'{', '}': b'}', '[': b'[', ']': b']', '˘': b'\xf9',
                '•': b'\xa5', 'c': b'c', 'ˇ': b'\xff', 'ç': b'\x8d', '¸': b'\xfc', '¢': b'\xa2', 'ˆ': b'\xf6',
                ':': b':', ',': b',', '©': b'\xa9', '¤': b'\xdb', 'd': b'd', '†': b'\xa0', '‡': b'\xe0', '°': b'\xfb',
                '¨': b'\xac', '÷': b'\xd6', '$': b'$', '˙': b'\xfa', 'ı': b'\xf5', 'e': b'e', 'é': b'\x8e',
                'ê': b'\x90', 'ë': b'\x91', 'è': b'\x8f', '8': b'8', '…': b'\xc9', '—': b'\xd1', '–': b'\xd0',
                '=': b'=', '!': b'!', '¡': b'\xc1', 'f': b'f', 'ﬁ': b'\xde', '5': b'5', 'ﬂ': b'\xdf', 'ƒ': b'\xc4',
                '4': b'4', '⁄': b'\xda', 'g': b'g', 'ß': b'\xa7', '`': b'`', '>': b'>', '«': b'\xc7', '»': b'\xc8',
                '‹': b'\xdc', '›': b'\xdd', 'h': b'h', '˝': b'\xfd', '-': b'-', 'i': b'i', 'í': b'\x92', 'î': b'\x94',
                'ï': b'\x95', 'ì': b'\x93', 'j': b'j', 'k': b'k', 'l': b'l', '<': b'<', '¬': b'\xc2', 'm': b'm',
                '¯': b'\xf8', 'μ': b'\xb5', 'n': b'n', '9': b'9', 'ñ': b'\x96', '#': b'#', 'o': b'o', 'ó': b'\x97',
                'ô': b'\x99', 'ö': b'\x9a', 'œ': b'\xcf', '˛': b'\xfe', 'ò': b'\x98', '1': b'1', 'ª': b'\xbb',
                'º': b'\xbc', 'ø': b'\xbf', 'õ': b'\x9b', 'p': b'p', '¶': b'\xa6', '(': b'(', ')': b')', '%': b'%',
                '.': b'.', '·': b'\xe1', '‰': b'\xe4', '+': b'+', '±': b'\xb1', 'q': b'q', '?': b'?', '¿': b'\xc0',
                '"': b'"', '„': b'\xe3', '“': b'\xd2', '”': b'\xd3', '‘': b'\xd4', '’': b'\xd5', '‚': b'\xe2',
                "'": b"'", 'r': b'r', '®': b'\xa8', 's': b's', '§': b'\xa4', ';': b';', '7': b'7', '6': b'6', '/': b'/',
                '\xa0': b' ', '£': b'\xa3', 't': b't', '3': b'3', '˜': b'\xf7', '™': b'\xaa', '2': b'2', 'u': b'u',
                'ú': b'\x9c', 'û': b'\x9e', 'ü': b'\x9f', 'ù': b'\x9d', '_': b'_', 'v': b'v', 'w': b'w', 'x': b'x',
                'y': b'y', 'ÿ': b'\xd8', '¥': b'\xb4', 'z': b'z', '0': b'0'}


decode_table = {v[0]: k for k, v in encode_table.items()}


def encode(text: str) -> Tuple[bytes, int]:
    return b''.join(encode_table.get(x, x.encode("latin1", 'replace')) for x in text), len(text)


def decode(binary: bytes) -> Tuple[str, int]:
    return ''.join(decode_table.get(x, chr(x)) for x in binary), len(binary)


def search(encoding_name):
    return codecs.CodecInfo(encode, decode, name=MacRomanEncoding)


