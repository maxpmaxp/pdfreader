from ..filters import apply_filter
from ..types.imagesaver import PILImageMixin


class StreamContent(object):
    pass


class TextObject(StreamContent):
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

    def __init__(self, source, strings, operators):
        self.source = source
        self.strings = strings
        self.operators = operators

    def to_string(self, glue=""):
        return glue.join(self.strings)


class InlineImage(PILImageMixin, StreamContent):
    """ BI/EI data

        Inline image looks like a stream-based object but really it is not.
        We just follow Stream interface to have an option to interact with InlineImage
        the same way as with XObject/Image

    """

    def __init__(self, entries, data):
        self.dictionary = entries
        self.data = data

    @property
    def Filter(self):
        return self.dictionary.get('Filter') or self.dictionary.get('F')

    @property
    def Width(self):
        return self.dictionary.get('Width') or self.dictionary.get('W')

    @property
    def Height(self):
        return self.dictionary.get('Height') or self.dictionary.get('H')

    @property
    def ColorSpace(self):
        return self.dictionary.get('ColorSpace') or self.dictionary.get('CS')

    @property
    def BitsPerComponent(self):
        return self.dictionary.get('BitsPerComponent') or self.dictionary.get('BPC')

    @property
    def Decode(self):
        return self.dictionary.get('Decode') or self.dictionary.get('D')

    @property
    def DecodeParms(self):
        return self.dictionary.get('DecodeParms') or self.dictionary.get('DP')

    @property
    def Intent(self):
        return self.dictionary.get('Intent')

    @property
    def Interpolate(self):
        return self.dictionary.get('Interpolate') or self.dictionary.get('I')

    @property
    def ImageMask(self):
        return self.dictionary.get('ImageMask') or self.dictionary.get('IM')

    @property
    def filtered(self):
        binary = self.data
        if self.Filter:
            binary = apply_filter(self.Filter, binary, self.dictionary.get('DecodeParms'))
        return binary


class Operator(object):
    """ Content stream operator """
    def __init__(self, name, args):
        self.name = name
        self.args = args


if __name__ == "__main__":
    import doctest
    doctest.testmod()
