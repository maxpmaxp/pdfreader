import logging

from typing import List
from copy import deepcopy


class GraphicsState(object):

    def __init__(self, **kwargs):
        # See PDF 1.7 specification sec. 8.4 - Graphics state
        # We don't care about most of the attrs. Tf is in use only at this time.

        # Attrs managed by graphics state commands
        self.CTM = None  # current transformation matrix
        self.LW = None  # line width
        self.LC = None  # line cap
        self.LJ = None  # line join style
        self.ML = None  # miter limit
        self.D = None  # line dash
        self.RI = None  # color rendering intent
        self.I = None  # flatness tolerance

        # See PDF 1.7 specification sec. 9.3 - Text State Parameters and Operators
        self.Font = None  # shall be a list if exists - [font_name, font_size] (Tf operator)
        self.Tc = 0     # char spacing
        self.Tw = 0     # word spacing
        self.Tz = 0     # horizontla scaling
        self.TL = 0     # text leading
        self.Tr = 0     # text rendering mode
        self.Ts = 0     # text rise

        # There are lot of other not supported attrs
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def font_name(self):
        if self.Font:
            return self.Font[0]


class GraphicsStateStack(List[GraphicsState]):

    def save_state(self):
        if self:
            self.append(deepcopy(self[-1]))
        else:
            logging.warning("Can't save empty state")

    def restore_state(self):
        if self:
            self.pop()
        else:
            logging.warning("Can't reset empty state")

    def _get_state(self):
        if not self:
            # create an empty instance
            self.append(GraphicsState())
        return self[-1]

    def _set_state(self, val: GraphicsState):
        if self:
            self.pop()
        self.append(val)

    state = property(_get_state, _set_state)
