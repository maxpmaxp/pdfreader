from decimal import Decimal

null = None
Boolean = bool
Integer = int
Real = Decimal
Array = list
Dictionary = dict


class String(str):
    """ Literal string. Just to tell apart of the other types """


class Name(str):
    """ Name type: /SomeName """


class HexString(String):
    """ Hexadecimal string: <AF20FA> """


class Stream(object):
    """ binary stream: dictionary and binary data
        common keys:
        Length - integer (required)
        Filter - name or array
        DecodeParams - dict or array
        F - file specification
        FFilter -

    """

    def __init__(self, info_dict, binary_stream):
        assert isinstance(info_dict, Dictionary)
        assert isinstance(binary_stream, bytes)

        if "Length" not in info_dict:
            raise KeyError("Missing stream length")

        if info_dict["Length"] != len(binary_stream):
            raise ValueError("Inconsistend stream")

        self.dictionary = info_dict
        self.stream = binary_stream

    def __len__(self):
        return len(self.stream)


class Comment(str):
    """ % Some PDF Comment """


class ObjRef(object):
    def __init__(self, number, generation):
        """ 10 0 R """
        assert isinstance(number, int)
        assert isinstance(generation, int) and generation >= 0

        self.num = number
        self.gen = generation


class IndirectObject(object):
    """ 10 0 obj
        ....
        endobj
    """
    def __init__(self, number, generation, value):
        assert isinstance(number, int)
        assert isinstance(generation, int) and generation >= 0
        assert isinstance(value,
                          (type(null), Boolean, Integer, Real, Array, Dictionary, String, Name, HexString, Stream,
                           ObjRef))
        self.num = number
        self.gen = generation
        self.val = value

    def __repr__(self):
        return "<IndirectObject:n={self.num},g={self.gen},v={val}>".format(self=self, val=repr(self.val))





