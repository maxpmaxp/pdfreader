from .codec import Codec


class StandardCodec(Codec):
    use_ZapfDingbats = True
    name = "StandardEncoding"

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

    decode_table = {65: 'A', 225: 'AE', 66: 'B', 67: 'C', 68: 'D', 69: 'E', 70: 'F', 71: 'G', 72: 'H', 73: 'I', 74: 'J',
                    75: 'K', 76: 'L', 232: 'Lslash', 77: 'M', 78: 'N', 79: 'O', 234: 'OE', 233: 'Oslash', 80: 'P', 81: 'Q',
                    82: 'R', 83: 'S', 84: 'T', 85: 'U', 86: 'V', 87: 'W', 88: 'X', 89: 'Y', 90: 'Z', 97: 'a',
                    194: 'acute', 241: 'ae', 38: 'ampersand', 94: 'asciicircum', 126: 'asciitilde', 42: 'asterisk',
                    64: 'at', 98: 'b', 92: 'backslash', 124: 'bar', 123: 'braceleft', 125: 'braceright', 91: 'bracketleft',
                    93: 'bracketright', 198: 'breve', 183: 'bullet (3)', 99: 'c', 207: 'caron', 203: 'cedilla', 162: 'cent',
                    195: 'circumflex', 58: 'colon', 44: 'comma', 168: 'currency1', 100: 'd', 178: 'dagger',
                    179: 'daggerdbl', 200: 'dieresis', 36: 'dollar', 199: 'dotaccent', 245: 'dotlessi', 101: 'e',
                    56: 'eight', 188: 'ellipsis', 208: 'emdash', 177: 'endash', 61: 'equal', 33: 'exclam',
                    161: 'exclamdown', 102: 'f', 174: 'fi', 53: 'five', 175: 'fl', 166: 'florin', 52: 'four',
                    164: 'fraction', 103: 'g', 251: 'germandbls', 193: 'grave', 62: 'greater', 171: 'guillemotleft',
                    187: 'guillemotright', 172: 'guilsinglleft', 173: 'guilsinglright', 104: 'h', 205: 'hungarumlaut',
                    45: 'hyphen', 105: 'i', 106: 'j', 107: 'k', 108: 'l', 60: 'less', 248: 'lslash', 109: 'm',
                    197: 'macron', 110: 'n', 57: 'nine', 35: 'numbersign', 111: 'o', 250: 'oe', 206: 'ogonek', 49: 'one',
                    227: 'ordfeminine', 235: 'ordmasculine', 249: 'oslash', 112: 'p', 182: 'paragraph', 40: 'parenleft',
                    41: 'parenright', 37: 'percent', 46: 'period', 180: 'periodcentered', 189: 'perthousand',
                    43: 'plus', 113: 'q', 63: 'question', 191: 'questiondown', 34: 'quotedbl', 185: 'quotedblbase',
                    170: 'quotedblleft', 186: 'quotedblright', 96: 'quoteleft', 39: 'quoteright', 184: 'quotesinglbase',
                    169: 'quotesingle', 114: 'r', 202: 'ring', 115: 's', 167: 'section', 59: 'semicolon', 55: 'seven',
                    54: 'six', 47: 'slash', 32: 'space', 163: 'sterling', 116: 't', 51: 'three', 196: 'tilde',
                    50: 'two', 117: 'u', 95: 'underscore', 118: 'v', 119: 'w', 120: 'x', 121: 'y', 165: 'yen', 122: 'z',
                    48: 'zero'}

