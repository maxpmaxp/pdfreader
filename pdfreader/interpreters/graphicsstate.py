from typing import List


class GraphicsState(object):
    # See PDF 1.7 specification sec. 8.4 - Graphics state
    # We don't care about most of the attrs. Tf is in use only at this time.

    # See PDF 1.7 specification sec. 9.3 - Text State Parameters and Operators
    Tc = None
    Tw = None
    Th = None
    Tl = None
    Tf = None # shall be a list if exists - [font_name, font_size]
    Tmode = None
    Trise = None
    Tk = None

    def __init__(self, **kwargs):
        for k, v in kwargs:
            setattr(self, k, v)

    @classmethod
    def from_ExtGState(cls, egs):
        """ Creates GraphicsState instance from ExtGState object.
            See PDF 1.7 specification sec. 8.4.5
        """
        kwargs = dict()
        if egs.Font:
            kwargs['Tf'] = egs.Font
        # ToDo: support another graphics state options
        return cls(**kwargs)

    @property
    def font_name(self):
        if self.Tf:
            return self.Tf[0]


class GraphicsStateStack(List[GraphicsState]):

    def execute_operator(self, op):
        pass

