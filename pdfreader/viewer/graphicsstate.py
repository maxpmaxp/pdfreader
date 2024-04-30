import logging
log = logging.getLogger(__name__)

from typing import List
from copy import deepcopy


class GraphicsState(object):
    """ Viewer's graphics state. See PDF 1.7 specification

    `sec. 8.4 - Graphics state <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=121>`_

    `sec. 9.3 - Text State Parameters and Operators <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=243>`_

    :param kwargs: dict of attributes to set
    """

    #: current transformation matrix
    CTM = None
    #: line width
    LW = None
    #: line cap
    LC = None
    #: line join style
    LJ = None
    #: miter limit
    ML = None
    #: line dash
    D = None
    #: color rendering intent
    RI = None
    #: flatness tolerance
    I = None

    #: shall be a list if exists - [font_name, font_size] (Tf operator)
    Font = None
    #: char spacing
    Tc = None
    #: word spacing
    Tw = None
    #: horizontlal scaling
    Tz = None
    #: text leading
    TL = None
    #: text rendering mode
    Tr = None
    #: text rise
    Ts = None

    _fields = ('CTM', 'LW', 'LC', 'LJ', 'ML', 'D', 'RI', 'I', 'Font', 'Tc', 'Tw', 'Tz', 'TL', 'Tr', 'Ts')

    def __init__(self, **kwargs):

        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def font_name(self):
        if self.Font:
            return self.Font[0]

    def update(self, other):
        for f in self._fields:
            val = getattr(other, f, None)
            if val is not None:
                setattr(self, f, val)


class GraphicsStateStack(List[GraphicsState]):
    """ Graphics state stack.
    See PDF 1.7 specification
    `sec. 8.4.2 - Graphics State Stack <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=124>`_

    """

    def save_state(self):
        """ Copies current state and puts it on the top """
        self.append(deepcopy(self.state))

    def restore_state(self):
        """ Restore previously saved state from the top """
        if self:
            self.pop()
        else:
            log.debug("Can't reset empty state")

    def _get_state(self):
        if not self:
            # create an empty instance
            self.append(GraphicsState())
        return self[-1]

    def _set_state(self, val: GraphicsState):
        if self:
            self.pop()
        self.append(val)

    #: Sets/gets current graphics state, which is on the top of the stack.
    state = property(_get_state, _set_state)
