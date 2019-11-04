import codecs

from typing import Tuple

StandardEncoding = "StandardEncoding"

encode_table = {'A': b'A', 'Æ': b'\xe1', 'B': b'B', 'C': b'C', 'D': b'D', 'E': b'E', 'F': b'F', 'G': b'G', 'H': b'H',
                'I': b'I', 'J': b'J', 'K': b'K', 'L': b'L', 'Ł': b'\xe8', 'M': b'M', 'N': b'N', 'O': b'O',
                'Œ': b'\xea', 'Ø': b'\xe9', 'P': b'P', 'Q': b'Q', 'R': b'R', 'S': b'S', 'T': b'T', 'U': b'U',
                'V': b'V', 'W': b'W', 'X': b'X', 'Y': b'Y', 'Z': b'Z', 'a': b'a', '´': b'\xc2', 'æ': b'\xf1', '&': b'&',
                '^': b'^', '~': b'~', '*': b'*', '@': b'@', 'b': b'b', '\\': b'\\', '|': b'|', '{': b'{', '}': b'}',
                '[': b'[', ']': b']', '˘': b'\xc6', '•': b'\xb7', 'c': b'c', 'ˇ': b'\xcf', '¸': b'\xcb', '¢': b'\xa2',
                'ˆ': b'\xc3', ':': b':', ',': b',', '¤': b'\xa8', 'd': b'd', '†': b'\xb2', '‡': b'\xb3', '¨': b'\xc8',
                '$': b'$', '˙': b'\xc7', 'ı': b'\xf5', 'e': b'e', '8': b'8', '…': b'\xbc', '—': b'\xd0', '–': b'\xb1',
                '=': b'=', '!': b'!', '¡': b'\xa1', 'f': b'f', 'ﬁ': b'\xae', '5': b'5', 'ﬂ': b'\xaf', 'ƒ': b'\xa6',
                '4': b'4', '⁄': b'\xa4', 'g': b'g', 'ß': b'\xfb', '`': b'\xc1', '>': b'>', '«': b'\xab', '»': b'\xbb',
                '‹': b'\xac', '›': b'\xad', 'h': b'h', '˝': b'\xcd', '-': b'-', 'i': b'i', 'j': b'j', 'k': b'k',
                'l': b'l', '<': b'<', 'ł': b'\xf8', 'm': b'm', '¯': b'\xc5', 'n': b'n', '9': b'9', '#': b'#', 'o': b'o',
                'œ': b'\xfa', '˛': b'\xce', '1': b'1', 'ª': b'\xe3', 'º': b'\xeb', 'ø': b'\xf9', 'p': b'p',
                '¶': b'\xb6', '(': b'(', ')': b')', '%': b'%', '.': b'.', '·': b'\xb4', '‰': b'\xbd', '+': b'+',
                'q': b'q', '?': b'?', '¿': b'\xbf', '"': b'"', '„': b'\xb9', '“': b'\xaa', '”': b'\xba', '‘': b'`',
                '’': b"'", '‚': b'\xb8', "'": b'\xa9', 'r': b'r', '°': b'\xca', 's': b's', '§': b'\xa7', ';': b';',
                '7': b'7', '6': b'6', '/': b'/', '\xa0': b' ', '£': b'\xa3', 't': b't', '3': b'3', '˜': b'\xc4',
                '2': b'2', 'u': b'u', '_': b'_', 'v': b'v', 'w': b'w', 'x': b'x', 'y': b'y', '¥': b'\xa5', 'z': b'z',
                '0': b'0'}

decode_table = {v[0]: k for k, v in encode_table.items()}


def encode(text: str) -> Tuple[bytes, int]:
    return b''.join(encode_table.get(x, x.encode("latin1", 'replace')) for x in text), len(text)


def decode(binary: bytes) -> Tuple[str, int]:
    return ''.join(decode_table.get(x, chr(x)) for x in binary), len(binary)


def search(encoding_name):
    return codecs.CodecInfo(encode, decode, name=StandardEncoding)


