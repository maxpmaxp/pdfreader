DEFAULT_ENCODING = "latin-1"

NULL = b'\x00'
TAB = b'\x09'
LF = b'\x0a' # \n
FF = b'\x0c'
CR = b'\x0d' # \r
SP = b'\x20'

DELIMITERS = (b'(', b')', b'<', b'>', b'[', b']', b'{', b'}', b'/', b'%')
WHITESPACES = (NULL, TAB, LF, FF, CR, SP)

WHITESPACE_CODES = [ord(c) for c in WHITESPACES]

EOL = (CR + LF, LF + CR, CR, LF)

TYPE_BOOL = "bool"
TYPE_INT = "int"
TYPE_REAL = "real"
TYPE_INSTRUCTION = "instruction"
TYPE_STRING = "string"
TYPE_HEXSTRING = "hexstring"
TYPE_ARRAY = "array"
TYPE_DICT = "dict"
TYPE_COMMENT = "comment"
TYPE_NAME = "name"
TYPE_STREAM = "stream"
TYPE_NULL = "null"

# String Escaped Chars
# \n       | LINE FEED (0Ah) (LF)
# \r       | CARRIAGE RETURN (0Dh) (CR)
# \t       | HORIZONTAL TAB (09h) (HT)
# \b       | BACKSPACE (08h) (BS)
# \f       | FORM FEED (FF)
# \(       | LEFT PARENTHESIS (28h)
# \)       | RIGHT PARENTHESIS (29h)
# \\       | REVERSE SOLIDUS (5Ch) (Backslash)
# \ddd     | Character code ddd (octal)

STRING_ESCAPED = {b'n': b"\n",
                  b'r': b"\r",
                  b't': b"\t",
                  b'b': b"\x08",
                  b'f': b"\x0c",
                  b'(': b"(",
                  b')': b")",
                  b'\\':b"\\"}

ESCAPED_CHARS = {"\n": "\\n",
                 "\r": "\\r",
                 "\t": "\\t",
                 "\x08": "\\b",
                 "\x0c": "\\f",
                 "(": "\\(",
                 ")": "\\)",
                 "\\": "\\\\"}

# maps predefined cmap name to character collection
predefined_cmap_names = {
    # Chinese (simplified)
    'GB-EUK-H': 'Adobe-GB1-0',
    'GB-EUK-V': 'Adobe-GB1-0',
    'GBpc-EUK-H': 'Adobe-GB1-0',
    'GBpc-EUK-V': 'Adobe-GB1-0',
    'GBK-EUK-H': 'Adobe-GB1-2',
    'GBKp-EUK-V': 'Adobe-GB1-2',
    'GBK2K-EUK-H': 'Adobe-GB1-4',
    'GBK2K-EUK-V': 'Adobe-GB1-4',
    'UniGB-UCS2-H': 'Adobe-GB1-4',
    'UniGB-UCS2-V': 'Adobe-GB1-4',
    'UniGB-UTF16-H': 'Adobe-GB1-4',
    'UniGB-UTF16-V': 'Adobe-GB1-4',
    # Chinese (traditional)
    'B5pc-H': 'Adobe-CNS1-0',
    'B5pc-V': 'Adobe-CNS1-0',
    'HKscs-B5-H': 'Adobe-CNS1-3',
    'HKscs-B5-V': 'Adobe-CNS1-3',
    'ETen-B5-H': 'Adobe-CNS1-0',
    'ETen-B5-V': 'Adobe-CNS1-0',
    'ETenms-B5-H': 'Adobe-CNS1-0',
    'ETenms-B5-V': 'Adobe-CNS1-0',
    'CNS-EUC-H': 'Adobe-CNS1-0',
    'CNS-EUC-V': 'Adobe-CNS1-0',
    'UniCNS-UCS2-H': 'Adobe-CNS1-3',
    'UniCNS-UCS2-V': 'Adobe-CNS1-3',
    'UniCNS-UTF16-H': 'Adobe-CNS1-4',
    'UniCNS-UTF16-V': 'Adobe-CNS1-4',
    # Japanese
    '83pv-RKSJ-H': 'Adobe-Japan1-1',
    '83pv-RKSJ-V': 'Adobe-Japan1-1',
    '90ms-RKSJ-H': 'Adobe-Japan1-2',
    '90ms-RKSJ-V': 'Adobe-Japan1-2',
    '90msp-RKSJ-H': 'Adobe-Japan1-2',
    '90msp-RKSJ-V': 'Adobe-Japan1-2',
    '90pv-RKSJ-H': 'Adobe-Japan1-1',
    '90pv-RKSJ-V': 'Adobe-Japan1-1',
    'Add-RKSJ-H': 'Adobe-Japan1-1',
    'Add-RKSJ-V': 'Adobe-Japan1-1',
    'EUC-H': 'Adobe-Japan1-1',
    'EUC-V': 'Adobe-Japan1-1',
    'Ext-RKSJ-H': 'Adobe-Japan1-2',
    'Ext-RKSJ-V': 'Adobe-Japan1-2',
    'H': 'Adobe-Japan1-1',
    'V': 'Adobe-Japan1-1',
    'UniJIS-UCS2-H': 'Adobe-Japan1-4',
    'UniJIS-UCS2-V': 'Adobe-Japan1-4',
    'UniJIS-UCS2-HW-H': 'Adobe-Japan1-4',
    'UniJIS-UCS2-HW-V': 'Adobe-Japan1-4',
    'UniJIS-UTF16-H': 'Adobe-Japan1-5',
    'UniJIS-UTF16-V': 'Adobe-Japan1-5',
    # Korean
    'KSC-EUC-H': 'Adobe-Korea1-0',
    'KSC-EUC-V': 'Adobe-Korea1-0',
    'KSCms-UHC-H': 'Adobe-Korea1-1',
    'KSCms-UHC-V': 'Adobe-Korea1-1',
    'KSCms-UHC-HW-H': 'Adobe-Korea1-1',
    'KSCms-UHC-HW-V': 'Adobe-Korea1-1',
    'KSCpc-EUC-H': 'Adobe-Korea1-0',
    'KSCpc-EUC-V': 'Adobe-Korea1-0',
    'UniKS-UCS2-H': 'Adobe-Korea1-1',
    'UniKS-UCS2-V': 'Adobe-Korea1-1',
    'UniKS-UTF16-H': 'Adobe-Korea1-2',
    'UniKS-UTF16-V': 'Adobe-Korea1-2',
    # Generic
    'Identity-H': 'Identity-H',
    'Identity-V': 'Identity-H'
}