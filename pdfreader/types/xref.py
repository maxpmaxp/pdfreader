import logging
log = logging.getLogger(__name__)

from collections import OrderedDict

MAX_GEN = 65535

TYPE_FREE = 0
TYPE_IN_USE = 1
TYPE_COMPRESSED = 2
KNOWN_TYPES = (TYPE_COMPRESSED, TYPE_IN_USE, TYPE_FREE)


class BaseXrefEntry(object):

    def __init__(self, number, generation=0, typ=None):
        assert isinstance(number, int) and number >= 0
        assert isinstance(generation, int) and generation >= 0

        if generation > MAX_GEN:
            log.warning("Incorrect generation {} for entry {}".format(generation, number))

        self.number = number
        self.generation = generation
        self.type = typ

    @property
    def is_in_use(self):
        return self.type == TYPE_IN_USE

    @property
    def is_free(self):
        return self.type == TYPE_FREE

    @property
    def is_compressed(self):
        return self.type == TYPE_COMPRESSED

    @property
    def is_unknown(self):
        return self.type not in KNOWN_TYPES


class XRefEntry(BaseXrefEntry):
    """ Regular Xref entry. Simple trailer table entry.
        No compressed objects support
    """
    def __init__(self, offset, number, generation, typ):
        if not (isinstance(offset, int) and offset >=0):
            raise AssertionError
        self.offset = offset
        if typ == 'n':
            typ = TYPE_IN_USE
        elif typ == 'f':
            typ = TYPE_FREE
        super(XRefEntry, self).__init__(number, generation, typ)

    def __repr__(self):
        return "<XRefEntry:number={s.number},generation={s.generation},offset={s.offset},type={s.type}>".format(s=self)


class CompressedObjEntry(BaseXrefEntry):
    """ Entry in compressed objects
        Generation is always 0 for compressed objects.
    """
    def __init__(self, number, index):
        if not (isinstance(index, int) and index >= 0):
            raise AssertionError
        self.index = index
        super(CompressedObjEntry, self).__init__(number, typ=TYPE_COMPRESSED)

    def __repr__(self):
        return "<XRefEntry(compressed):number={s.number},generation={s.generation},index={s.index},type={s.type}>"\
            .format(s=self)


class XRef(object):
    """ xref - Cross reference entry """

    def __init__(self):
        # According to the specification free objexts must be implemented as a linked list
        # But we don't care about that as we don't want to update PDFs. Just read.
        self.free = OrderedDict()
        self.in_use = OrderedDict()
        self.compressed = OrderedDict()

    @property
    def __len__(self):
        return len(self.free) + len(self.in_use) + len(self.compressed)

    def add_entry(self, entry):
        if entry.is_compressed:
            self.compressed[entry.number] = entry
        elif entry.is_free:
            self.free[entry.number] = entry
        elif entry.is_in_use:
            self.in_use[entry.number] = entry

    def merge(self, other):
        for xre in other.free.values():
            self.add_entry(xre)
        for xre in other.in_use.values():
            self.add_entry(xre)
        for xre in other.free.values():
            self.add_entry(xre)
        for xre in other.compressed.values():
            self.add_entry(xre)

    def __repr__(self):
        return "<XRef:free={},in_use={},compressed={}>".format(len(self.free), len(self.in_use), len(self.compressed))

    @classmethod
    def from_stream(cls, stream):
        self = cls()
        self.compressed = {}
        self._stream = stream # Just for debugging, normally we don't need this.

        if stream.get("Index"):
            # ToDo: data/f8ben.pdf contains index of [226, 1, 250, 1, 299, 2, 302, 3]
            # ToDo: and the only meaningfull in_use entry. PDF 1.7 says here must be just 2 values.
            # ToDo: this must be interpreded some way. Need to investigate
            first_object, n_entries = stream["Index"][0:2]
        else:
            first_object, n_entries = 0, stream["Size"]
        colsizes = stream["W"]
        colsoffsets = [0, colsizes[0], colsizes[0] + colsizes[1]]
        rowsize = sum(colsizes)
        data = stream.filtered

        # walk rows
        objnum = first_object
        for i in range(0, len(data), rowsize):
            row = data[i:i+rowsize]
            cols, entry = [], None
            # extract columns
            for j in range(3):
                if colsizes[j] == 0:
                    # if colsize is 0 it means it's just absent
                    # 0 - default
                    v = 0
                else:
                    b = colsoffsets[j]
                    e = b + colsizes[j]
                    v = int.from_bytes(row[b:e], "big")
                cols.append(v)

            if cols[0] == 0:
                # free entry
                entry = XRefEntry(number=cols[1], generation=cols[2], offset=0, typ=TYPE_FREE)
            elif cols[0] == 1:
                # used entry
                entry = XRefEntry(number=objnum, generation=cols[2], offset=cols[1], typ=TYPE_IN_USE)
            elif cols[0] == 2:
                # compressed object
                entry = CompressedObjEntry(number=cols[1], index=cols[2])
            else:
                # PDF 1.5-1.7 defines any other reference types as references to null objects.
                # so we just skip those
                log.debug("Undefined xref col type (index 0): {}".format(cols))

            if entry is not None:
                self.add_entry(entry)
            objnum += 1

        return self
