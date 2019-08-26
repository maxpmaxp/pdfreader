from ..types import IndirectObject
from .base import BasicTypesParser


class ObjStmParser(BasicTypesParser):

    def objects(self, first_offset, n_objects):
        integers = []
        for i in range(2 * n_objects):
            self.maybe_spaces_or_comments()
            integers.append(self.non_negative_int())

        for j in range(n_objects):
            num, offset = integers[2 * j: 2 * j + 2]
            self.reset(first_offset + offset)
            yield IndirectObject(num, 0, self.object())
