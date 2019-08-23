import logging

from .parser import PDFParser
from .types import Stream, IndirectObject


class Registry(object):

    """ Registry of known indirect objects  """

    def __init__(self):
        self.known_indirect_objects = dict()
        # id -> begin/end offsets. End means the next byte after obj
        # this may help to implement different indirect references resolution strategies
        self.indirect_object_offsets = dict()
        self.next_brute_force_offset = None

    def is_registered(self, n, gen):
        return (n, gen) in self.known_indirect_objects

    def register(self, obj, b_offset=None, e_offset=None):
        if not self.is_registered(obj.num, obj.gen):
            key = obj.num, obj.gen
            self.known_indirect_objects[key] = obj.val
            self.indirect_object_offsets[key] = (b_offset, e_offset)
            logging.info("Indirect object registered: {key} -> {val}".format(key=key, val=obj.val))

            if isinstance(obj.val, Stream):
                if obj.val.get("Type") == "ObjStm":
                    self.register_object_stream(obj.val)

    def get(self, n, gen):
        key = n, gen
        return self.known_indirect_objects.get(key)

    def __getitem__(self, key):
        return self.known_indirect_objects[key]

    def register_object_stream(self, objstm):
        parser = PDFParser(objstm.filtered)
        first_offset = objstm["First"]
        n_objects = objstm["N"]
        # read 2 * n_objects integers which are pairs (obj_num, obj_offset_relative_to_first)
        integers = []

        for i in range(2 * n_objects):
            parser.maybe_spaces_or_comments()
            integers.append(parser.non_negative_int())

        for j in range(n_objects):
            num, offset = integers[2 * j: 2 * j + 2]
            parser.reset(first_offset + offset)
            val = parser.object()
            # generation is always 0 for compressed objects
            self.register(IndirectObject(num, 0, val))