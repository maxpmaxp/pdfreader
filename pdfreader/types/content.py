from PIL import Image

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
    def Filter(self):
        return self.entries.get('Filter') or self.entries.get('F')

    @property
    def Width(self):
        return self.entries.get('Width') or self.entries.get('W')

    @property
    def Height(self):
        return self.entries.get('Height') or self.entries.get('H')

    @property
    def ColorSpace(self):
        return self.entries.get('ColorSpace') or self.entries.get('CS')

    @property
    def BitsPerComponent(self):
        return self.entries.get('BitsPerComponent') or self.entries.get('BPC')

    @property
    def Decode(self):
        return self.entries.get('Decode') or self.entries.get('D')

    @property
    def DecodeParms(self):
        return self.entries.get('DecodeParms') or self.entries.get('DP')

    @property
    def Intent(self):
        return self.entries.get('Intent')

    @property
    def Interpolate(self):
        return self.entries.get('Interpolate') or self.entries.get('I')

    @property
    def filtered(self):
        binary = self.data
        if self.Filter:
            binary = apply_filter(self.Filter, binary, self.entries.get('DecodeParms'))
        return binary

    def save(self, name):
        size = self.Width, self.Height

        if self.ColorSpace in ('DeviceRGB', 'RGB'):
            mode = "RGB"
        else:
            mode = "P"

        img = Image.frombytes(mode, size, self.filtered)
        img.save(name)


