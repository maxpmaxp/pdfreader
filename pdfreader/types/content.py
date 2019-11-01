
class TextObject(object):
    """ BT/ET data """

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
