from ..types.imagesaver import ImageSaverMixin


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


class InlineImage(ImageSaverMixin):
    """ BI/EI data

        >>> import pkg_resources
        >>> entries = {'D': [1, 0], 'IM': True, 'W': 128, 'H': 128, 'BPC': 1, 'F': 'RL'}
        >>> with pkg_resources.resource_stream('pdfreader', 'types/samples/inline-image-0.data') as fd:
        ...     data = fd.read()
        >>> img = InlineImage(entries, data)
        >>> len(img.filtered) == 2048
        True
        >>> len(img.decoded) == 16384
        True
        >>> with open("111.png", "wb") as f:
        ...     img.save(f)

    """

    def __init__(self, entries, data):
        self.dictionary = entries
        self.data = data



if __name__ == "__main__":
    import doctest
    doctest.testmod()
