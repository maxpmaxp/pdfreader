
class StartXRef(object):
    """ startxref
        123

        Pseudo object. Can be between indirect objects if any incremental updates.
    """

    def __init__(self, offset):
        self.offset = offset

    def __repr__(self):
        return "<StartXRef: {}>".format(self.offset)

    def __eq__(self, other):
        return self.offset == other.offset


class Trailer(object):
    """ trailer
            <<< ... .>>
        endtrailer

        Pseudo object. Can be between indirect objects if any incremental updates.
        """
    def __init__(self, params):
        self.params = params

    def __repr__(self):
        return "<Trailer: {}>".format(self.params)

    def __eq__(self, other):
        return self.params == other.params