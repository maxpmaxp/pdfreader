import logging
from ..filters import apply_filter


class TextObject(object):
    """ BT/ET data

        The object is a bit tricky. It's goal to hold text content suitable for data extraction.
        That's why it contains:
        - decoded text
        - text flow/positioning/markup etc.

        instance.string - list of all string literals (decoded)
        instance.source - BT/ET section source containing decoded strings.
                          And here might be an issue. As flow/positioning/markup etc. commands, comments and args
                          are actually bytes, we decode it with DEFAULT_ENCODING to concat with decoded strings.

    """

    def __init__(self, source, strings):
        self.source = source
        self.strings = strings

    def to_string(self, glue=""):
        return glue.join(self.strings)


class InlineImage(object):
    """ BI/EI data """

    def __init__(self, entries, data):
        self.entries = entries
        self.data = data

    @property
    def filtered(self):
        filter_name = self.entries.get('Filter') or self.entries.get('F')
        binary = self.data
        if filter_name:
            binary = apply_filter(filter_name, binary, self.entries.get('DecodeParms'))
        return binary
