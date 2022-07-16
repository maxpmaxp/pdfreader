import os
from io import BytesIO

from .exceptions import EOFException


class Buffer(object):
    """
    Buffer, that iterates bytes forward and backward from the file one by one taking care of reading more data.

    >>> from io import BytesIO
    >>> s = BytesIO(b"123")

    Test forward reading

    >>> b = Buffer(s, 0, 2)
    >>> b.next()
    b'1'
    >>> b.next()
    b'2'
    >>> b.next()
    b'3'
    >>> b.next() is None
    True

    >>> b = Buffer(s, 1, 2)
    >>> b.next()
    b'2'
    >>> b.current
    b'3'
    >>> b.next()
    b'3'
    >>> b.next() is None
    True


    Test backward reading

    >>> b = Buffer(s, -2, 2)
    >>> b.prev()
    b'3'
    >>> b.current
    b'2'
    >>> b.prev()
    b'2'
    >>> b.prev()
    b'1'
    >>> b.prev() is None
    True


    Test forward/backward reading

    >>> b = Buffer(s, 1, 2)
    >>> b.current
    b'2'
    >>> b.prev()
    b'2'
    >>> b.current
    b'1'
    >>> b.next()
    b'1'
    >>> b.current
    b'2'

    Test reading

    >>> b = Buffer(s, 0, 2)
    >>> b.read(3)
    b'123'
    >>> b.current is None
    True

    >>> b = Buffer(s, 0, 2)
    >>> b.read(2)
    b'12'
    >>> b.current
    b'3'


    """

    state_attrs = ('offset', 'block_size', 'last_block_size', 'last_block_offset', 'index', 'data')

    def __init__(self, fileobj, offset, block_size=1024):
        self.fileobj = BytesIO(fileobj) if isinstance(fileobj, bytes) else fileobj
        self.offset = offset
        self.block_size = block_size
        self.last_block_size = None
        self.last_block_offset = None
        self.index = None
        self.data = b''
        self.reset(offset)
        self.stack = []

    def _read_forward(self):
        offset = self.last_block_offset + self.block_size
        self.fileobj.seek(offset)
        data = self.fileobj.read(self.block_size)
        if not (bool(data)):
            raise EOFException()
        self.last_block_size = len(data)
        self.last_block_offset += self.last_block_size
        self.data += data

    def _read_backward(self):
        if self.last_block_offset == 0:
            raise EOFException()
        size = min(self.last_block_offset, self.block_size)
        offset = self.last_block_offset - size
        self.fileobj.seek(offset)
        self.fileobj.seek(offset)
        data = self.fileobj.read(size)
        self.last_block_size = len(data)
        self.last_block_offset = offset
        self.index = self.last_block_size + self.index
        self.data = data + self.data

    def _read_head(self, offset):
        self.fileobj.seek(offset)
        data = self.fileobj.read(self.block_size)
        self.last_block_offset = offset
        self.last_block_size = len(data)
        self.data = data
        self.index = 0

    def _read_tail(self, offset):
        real_offset = self.fileobj.seek(offset, os.SEEK_END)
        data = self.fileobj.read()
        self.last_block_offset = real_offset
        self.last_block_size = len(data)
        self.data = data
        self.index = len(data) - 1

    def next(self):
        """ Returns current byte and moves pointer to the next byte """
        res = self.current
        self.index += 1
        return res

    def prev(self):
        """ Returns current byte and moves pointer to the previous byte """
        res = self.current
        self.index -= 1
        return res

    @property
    def current(self):
        try:
            if self.index >= len(self.data):
                self._read_forward()
            elif self.index < 0:
                self._read_backward()
            res = bytes([self.data[self.index]])
        except EOFException:
            res = None
        return res

    def reset(self, offset):
        if offset >= 0:
            self._read_head(offset)
        else:
            self._read_tail(offset)

    def read(self, n):
        return b''.join([self.next() for _ in range(n)])

    def read_backward(self, n):
        res = b''
        for _ in range(n): res = self.prev() + res
        return res

    @property
    def is_eof(self):
        return self.current is None

    def get_state(self):
        return {a: getattr(self, a) for a in self.state_attrs}

    def set_state(self, state):
        for k, v in state.items():
            setattr(self, k, v)
        self.fileobj.seek(self.last_block_offset)


if __name__ == "__main__":
    import doctest
    doctest.testmod()