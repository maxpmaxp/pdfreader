from .constants import PS_CHARNAMES
from .native import HexString


class Range(object):

    def __init__(self, begin: str, end: str):
        if len(begin) != len(end):
            raise AssertionError
        begin = HexString(begin)
        end = HexString(end)
        self.int_begin = begin.as_int
        self.int_end = end.as_int
        if self.int_begin > self.int_end:
            raise ValueError(begin)
        self.begin = begin.upper()
        self.end = end.upper()
        self.size = len(self.begin)

    def match_size(self, item: str):
        return len(item) == len(self.begin)

    def __contains__(self, item: HexString):
        """
        >>> HexString("0a") in Range("0A", "0F")
        True
        >>> HexString("0B") in Range("0A", "0F")
        True
        >>> HexString("00A") in Range("0A", "0F")
        False
        >>> HexString("10") in Range("0A", "0F")
        False
        >>> HexString("0a") in Range("000a", "000f")
        False
        >>> HexString("000C") in Range("000a", "000f")
        True
        >>> Range("000f", "000a")
        Traceback (most recent call last):
        ...
        ValueError: 000f
        """
        return len(item) == self.size and self.int_begin <= HexString(item).as_int <= self.int_end

    def __repr__(self):
        return "<Range:{self.begin}-{self.end}>".format(self=self)

    def __len__(self):
        """
        >>> len(Range("00", "00"))
        1
        >>> len(Range("0000", "00ff"))
        256
        """
        return self.int_end - self.int_begin + 1

    def __iter__(self):
        """
        >>> [v for v in Range("09", "0f")]
        ['09', '0A', '0B', '0C', '0D', '0E', '0F']
        """
        for i in range(self.int_begin, self.int_end+1):
            yield hex(i)[2:].upper().zfill(self.size)


class MapRange(Range):

    def __init__(self, begin: str, end: str, map_to_start: [int,str]):
        super(MapRange, self).__init__(begin, end)
        if isinstance(map_to_start, str):
            map_to_start = HexString(map_to_start).as_int
        self.map_to_start = map_to_start

    def __getitem__(self, item: str):
        """
        >>> r = MapRange("00", "04", 5)
        >>> r["00"], r["01"], r["04"]
        ('\\x05', '\\x06', '\\t')
        >>> r["05"]
        Traceback (most recent call last):
        ...
        KeyError: '05'
        >>> r = MapRange("00", "04", 0x10FFFF)
        >>> r["00"]
        '\U0010ffff'
        >>> r["01"], r["02"], r["03"], r["04"]
        ('�', '�', '�', '�')
        """
        if item not in self:
            raise KeyError(item)

        code = self.map_to_start + (HexString(item).as_int - self.int_begin)
        if 0 <= code <= 0x10FFFF:
            # valid unicode range
            val = chr(code)
        else:
            val = chr(0xFFFD) # unicode REPLACEMENT CHARACTER

        return val

    def get(self, item, default=None):
        """
        >>> r = MapRange("00", "04", "05")
        >>> r.get("00"), r.get("01", None), r.get("04")
        ('\\x05', '\\x06', '\\t')
        >>> r.get("05") is None
        True
        >>> r.get("05", -1)
        -1
        """
        try:
            res = self[item]
        except KeyError:
            res = default
        return res

    def __repr__(self):
        return "<MapRange:{self.begin}-{self.end},{self.map_to_start}>".format(self=self)


class BFChar(object):
    """ Single char mapped to code hex value or named char.
        Doesn't need to use int convertions.
        Follows MapRange interface
    """

    def __init__(self, begin: str, mapped: str):
        self.begin = begin.upper()
        self.mapped = mapped.upper() if not mapped.startswith("/") else mapped

    def match_size(self, item: str):
        return len(item) == len(self.begin)

    def __contains__(self, item: str):
        """
        >>> HexString("0a") in BFChar("0A", "FF00")
        True
        >>> HexString("0a") in BFChar("0A", "/yen")
        True
        >>> HexString("000a") in BFChar("0A", "/yen")
        False
        >>> HexString("0B") in BFChar("0A", "FF00")
        False
        """
        return item.upper() == self.begin

    def __repr__(self):
        return "<BFChar:{self.begin}:{self.mapped}>".format(self=self)

    def __len__(self):
        """
        >>> len(BFChar("00", "FF00"))
        1
        """
        return 1

    def __getitem__(self, item: str):
        """

        Single characted encoded

        >>> r = BFChar("00", "67")
        >>> r["00"]
        'g'

        >>> r = BFChar("0000", "AF00")
        >>> r["0000"]
        '꼀'

        BFChar may encode several characters:

        >>> r = BFChar("0000", "AF000067")
        >>> r["0000"]
        '꼀g'

        >>> r = BFChar("1E", "00660069")
        >>> r["1E"]
        'fi'

        It also may contain PostScript character names

        >>> r = BFChar("00", "/yen")
        >>> r["00"]
        '¥'

        >>> r = BFChar("35", "0035")
        >>> r["35"]
        '5'

        >>> r["05"]
        Traceback (most recent call last):
        ...
        KeyError: '05'
        >>> r["0000"]
        Traceback (most recent call last):
        ...
        KeyError: '0000'
        """
        if item != self.begin:
            raise KeyError(item)
        if self.mapped.startswith('/'):
            val = PS_CHARNAMES.get(self.mapped[1:], self.mapped)
        else:
            # decode
            val = "".join([chr(HexString(self.mapped[i:i+4]).as_int) for i in range(0, len(self.mapped), 4)])
        return val

    def get(self, item, default=None):
        """
        >>> r = BFChar("00", "/UnKn0Wn")
        >>> r.get("00")
        '/UnKn0Wn'
        >>> r.get("05", "/")
        '/'
        >>> r.get("0000") is None
        True
        """
        try:
            res = self[item]
        except KeyError:
            res = default
        return res


class CodespaceRanges(object):

    def __init__(self):
        self.ranges = []

    def __bool__(self):
        return bool(self.ranges)

    def __contains__(self, item: str):
        """
        >>> cr = CodespaceRanges()
        >>> cr.add(Range("02", "1E"))
        >>> cr.add(Range("FA", "FF"))
        >>> "0A" in cr
        True
        >>> "02" in cr
        True
        >>> '1E' in cr
        True
        >>> 'fb' in cr
        True
        >>> "2f" in cr
        False
        >>> "f9" in cr
        False
        >>> cr = CodespaceRanges()
        >>> cr.add(Range("02", "02"))
        >>> "02" in cr
        True
        >>> "03" in cr
        False
        """
        return any(item in r for r in self.ranges)

    def add(self, robj):
        self.ranges.append(robj)

    @property
    def max(self):
        """
        >>> cr = CodespaceRanges()
        >>> cr.add(Range("02", "1e"))
        >>> cr.add(Range("FA", "FF"))
        >>> cr.max
        255
        """
        return max(r.int_end for r in self.ranges)

    @property
    def as_list(self):
        """
        >>> cr = CodespaceRanges()
        >>> cr.add(Range('02', '05'))
        >>> cr.add(Range(HexString("FA"), HexString("FF")))
        >>> cr.as_list
        ['02', '03', '04', '05', 'FA', 'FB', 'FC', 'FD', 'FE', 'FF']
        """
        res = set()
        for r in self.ranges:
            int_range = sorted(list(range(r.int_begin, r.int_end + 1)))
            res.update([HexString(hex(n)[2:].upper().zfill(r.size)) for n in int_range])
        return sorted(res)

    def __len__(self):
        """
        >>> cr = CodespaceRanges()
        >>> cr.add(Range("02", "05"))
        >>> cr.add(Range(HexString("FA"), HexString("FF")))
        >>> len(cr)
        10
        """
        return len(self.as_list)

    def __repr__(self):
        rr = repr(self.ranges)
        if len(rr) > 50:
            rr = rr[:50] + " ..."
        return "<CodespaceRanges:ranges={}>".format(rr)

    def merge(self, other):
        """
        >>> cr1 = CodespaceRanges()
        >>> cr1.add(Range("02", "05"))
        >>> cr2 = CodespaceRanges()
        >>> cr2.add(Range("000A", "000B"))
        >>> cr1.merge(cr2)
        >>> cr1.as_list
        ['000A', '000B', '02', '03', '04', '05']
        """
        self.ranges.extend(other.ranges)


class MappedCodespaceRanges(CodespaceRanges):

    def __getitem__(self, item):
        """
        >>> r = MappedCodespaceRanges()
        >>> r.add(MapRange("00", "04", 5))
        >>> r.add(MapRange("06", "0A", 106))
        >>> r["00"], r["04"], r["06"], r["07"], r["08"]
        ('\\x05', '\\t', 'j', 'k', 'l')
        >>> r["05"]
        Traceback (most recent call last):
        ...
        KeyError: '05'
        >>> r["20"]
        Traceback (most recent call last):
        ...
        KeyError: '20'
        """
        for r in self.ranges:
            if item in r:
                return r[item]
        raise KeyError(item)

    def get(self, item, default=None):
        """
        >>> r = MappedCodespaceRanges()
        >>> r.add(MapRange("00", "04", 5))
        >>> r.add(MapRange('06', '0a', 106))
        >>> r.get('05') is None
        True
        >>> r.get('05', -1)
        -1
        >>> r.get('00'), r.get('04'), r.get('06', -1), r.get('07', None), r.get('08')
        ('\\x05', '\\t', 'j', 'k', 'l')
        """
        try:
            res = self[item]
        except KeyError:
            res = default
        return res

    @property
    def as_dict(self):
        """
        >>> r = MappedCodespaceRanges()
        >>> r.add(MapRange("00", "04", 5))
        >>> r.add(MapRange('06', '0a', 106))
        >>> r.as_dict == {'00': '\\x05', '01': '\\x06', '02': '\\x07', '03': '\\x08', '04': '\\t', '06': 'j', '07': 'k', '08': 'l', '09': 'm', '0A': 'n'}
        True
        """
        return {item: self[item] for item in self.as_list}

    def __repr__(self):
        rr = repr(self.ranges)
        if len(rr) > 50:
            rr = rr[:50] + " ..."
        return "<MappedCodespaceRanges:ranges={}>".format(rr)


class CMapResource(object):

    def __init__(self, name, codespace_ranges=None, cid_ranges=None, notdef_ranges=None, bf_ranges=None):
        self.name = name
        self.codespace_ranges=codespace_ranges
        self.cid_ranges = cid_ranges
        self.notdef_ranges = notdef_ranges
        self.bf_ranges = bf_ranges

    def __repr__(self):
        return "<CMapResource {self.name}:codespace_ranges={self.codespace_ranges!r}," \
               "cid_ranges={self.cid_ranges!r}," \
               "notdef_ranges={self.notdef_ranges!r}," \
               "bf_ranges={self.bf_ranges!r}>".format(self=self)




if __name__ == "__main__":
    import doctest
    doctest.testmod()
