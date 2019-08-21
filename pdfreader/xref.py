MAX_GEN = 65535


class XRefEntry(object):

    def __init__(self, offset, number, generation):
        assert isinstance(offset, int) and offset >=0
        assert isinstance(number, int) and number >=0
        assert isinstance(generation, int) and 0 <= generation <= MAX_GEN
        self.offset = offset
        self.number = number
        self.gen = generation


class XRef(object):
    """ xref - Cross reference entry """

    def __init__(self):
        self.free = dict()
        self.in_use = dict()

    @property
    def __len__(self):
        return len(self.free) + len(self.in_use)

    def add_entry(self, offset, number, generation, literal):
        assert literal in ('n', 'f')

        entry = XRefEntry(offset, number, generation)
        existing_free = self.free.get(number)
        existing_in_use = self.in_use.get(number)
        skip_entry = False
        if existing_free:
            if generation > existing_free.gen:
                self.free.pop(number)
            else:
                skip_entry = True
        if existing_in_use:
            if generation > existing_in_use.gen:
                self.in_use.pop(number)
            else:
                skip_entry = True

        if not skip_entry:
            target = self.free if literal == 'f' else self.in_use
            target[number] = entry

    def merge(self, other):
        for xr in other.free.values():
            self.add_entry(xr.offset, xr.number, xr.generation, 'f')
        for xr in other.in_use.values():
            self.add_entry(xr.offset, xr.number, xr.generation, 'n')

    def __repr__(self):
        return "<XRef:free={},in_use={}>".format(len(self.free), len(self.in_use))
