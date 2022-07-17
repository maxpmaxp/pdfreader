import logging
log = logging.getLogger(__name__)

from .parsers import ObjStmParser
from .types import Stream


class Registry(object):

    """ Registry of known indirect objects  """

    def __init__(self):
        self.known_indirect_objects = {}
        # id -> begin/end offsets. End means the next byte after obj
        # this may help to implement different indirect references resolution strategies
        self.indirect_object_offsets = {}
        self.next_brute_force_offset = None

    def is_registered(self, n, gen):
        return (n, gen) in self.known_indirect_objects

    def register(self, obj, b_offset=None, e_offset=None, force=False):
        if force or not self.is_registered(obj.num, obj.gen):
            key = obj.num, obj.gen
            self.known_indirect_objects[key] = obj.val
            self.indirect_object_offsets[key] = (b_offset, e_offset)
            log.debug("Indirect object registered: {key} -> {val}".format(key=key, val=obj.val))

            if isinstance(obj.val, Stream):
                if obj.val.get("Type") == "ObjStm":
                    log.debug("Registering ObjStm {}".format(key))
                    self.register_object_stream(obj.val)

    def get(self, n, gen):
        key = n, gen
        return self.known_indirect_objects.get(key)

    def __getitem__(self, key):
        return self.known_indirect_objects[key]

    def register_object_stream(self, objstm):
        parser = ObjStmParser(objstm.filtered)

        for obj in parser.objects(objstm["First"], objstm["N"]):
            # generation is always 0 for compressed objects
            self.register(obj)
            log.debug("Compressed object registered {} {}".format(obj.num, obj.gen))

