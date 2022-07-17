import logging
log = logging.getLogger(__name__)


filter_names = ('RunLengthDecode', 'RL')


def decode(data, *_):
    """
    >>> data = bytes([5, 65, 66, 67, 68, 69, 70, 250, 55, 2, 65, 66, 67, 252, 53, 128])
    >>> decode(data)
    b'ABCDEF7777777ABC55555'

    >>> data = bytes([5, 65])
    >>> decode(data)
    b''

    >>> data = bytes([128])
    >>> decode(data)
    b''
    """
    res = b''
    buffer = []
    state = 'need_length'
    for c in data:
        if state == 'need_length':
            if c == 128:
                state = 'done'
                break
            buffer = []
            length = c
            if c >= 129:
                state = 'need_one'
            else:
                state = 'need_many'
        elif state == 'need_one':
            res += bytes([c] * (257 - length))
            state = 'need_length'
        elif state == 'need_many':
            buffer.append(c)
            if len(buffer) == length + 1:
                res += bytes(buffer)
                buffer = []
                state = 'need_length'

    if state != 'done':
        log.error("Skipping broken stream")
        res = b''

    return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
