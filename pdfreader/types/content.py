from ..pillow import PILImageMixin
from ..types.native import apply_filter_multi


class StreamContent(object):

    @property
    def as_source_code(self):
        """ Shall return a string containing meaningful PDF source for the object """
        raise NotImplementedError


class InlineImage(PILImageMixin, StreamContent):
    """ BI/ID/EI operators content.

        Inline image looks like a stream-based object but really it is not.
        We just follow Stream interface to have an option to interact with InlineImage
        the same way as with XObject/Image

    """
    #: key-value image properties
    dictionary = None
    #: bytes, encoded image stream
    data = None

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
        """ :return: bytes, decoded image stream as it defined by image properties """
        return apply_filter_multi(self.Filter, self.data, self.DecodeParms)


class Operator(StreamContent):
    """ Page content stream operator. For example: */F01 12 Tf*

    """
    #: operator name
    name = None
    #: list of operands
    args = None

    def __init__(self, name, args):
        self.name = name
        self.args = args


if __name__ == "__main__":
    import doctest
    doctest.testmod()
