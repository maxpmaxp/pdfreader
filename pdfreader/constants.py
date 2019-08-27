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

STRING_ESCAPED = {b'n': "\n",
                  b'r': "\r",
                  b't': "\t",
                  b'b': "\x08",
                  b'f': "\x0c",
                  b'(': "(",
                  b')': ")",
                  b'\\': "\\"}

ESCAPED_CHARS = {"\n": "\\n",
                 "\r": "\\r",
                 "\t": "\\t",
                 "\x08": "\\b",
                 "\x0c": "\\f",
                 "(": "\\(",
                 ")": "\\)",
                 "\\": "\\\\"}