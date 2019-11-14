import logging

from copy import deepcopy

from .base import BasicTypesParser
from ..types.content import StreamContent, Operator
from ..types.graphicsstate import GraphicsState
from ..types.native import null, Token
from .inlineimage import InlineImageParser
from .text import TextParser


class ContentParser(BasicTypesParser):
    """ Page.Content parser """

    # ToDo: There is an architectural issue here: parsers must just parse streams
    # and some other class (Viewer/Interpreter) must take care of decoding.
    # Refactoring needed.

    def __init__(self, context, *args, **kwargs):
        self.context = context
        # potentially graphics state may be defined on Page description level
        # See PDF 1.7 specification sec. 8.4.2 - Graphics State Stack
        self.graphics_state_stack = []
        super(ContentParser, self).__init__(*args, **kwargs)

    @property
    def graphics_state(self):
        # current graphics state is on the top of graphics_state_stack
        if not self.graphics_state_stack:
            self.graphics_state_stack.append(GraphicsState())
        return self.graphics_state_stack[-1]

    def save_graphics_state(self):
        copy = deepcopy(self.graphics_state)
        self.graphics_state_stack.append(copy)

    def set_graphics_state(self, name):
        if self.graphics_state_stack:
            self.graphics_state_stack.pop()
        try:
            state = self.context.graphics_states[name]
            self.graphics_state_stack.append(state)
        except KeyError:
            logging.warning("Named graphics state was not found. Ignoring: {}".format(name))

    def restore_graphics_state(self):
        if self.graphics_state_stack:
            self.graphics_state_stack.pop()
        else:
            # q/Q commands shall be balanced within a given content stream or within the sequence of streams
            # specified by Content. But real-life examples show that `Q` sometimes comes after `do` without preceeding
            # `q`
            logging.debug("Can't restore graphics stack. It's empty. Leaving as is.")

    def objects(self):
        """ Returns list of content objects as they follow in the document """
        operands = []
        self.maybe_spaces_or_comments()
        while self.current:
            obj = self.object()
            if isinstance(obj, StreamContent):
                if operands:
                    logging.warning("Skipping unexpected operands: {}".format(operands))
                    operands = []
                yield obj
            elif self.is_operator(obj):
                op = Operator(obj, operands)
                self.execute(op)
                yield op
                operands = []
            else:
                operands.append(obj)
            self.maybe_spaces_or_comments()
        if operands:
            logging.warning("Skipping unexpected operands at the end of stream: {}".format(operands))

    def execute(self, op):
        if op.name == 'q':
            # push current graphics state on the top of stack
            self.save_graphics_state()
        elif op.name == 'Q':
            # restore previous current graphics state on the top of stack
            self.restore_graphics_state()
        elif op.name == 'gs':
            self.set_graphics_state(op.args[0])
        if op.name == "Tf":
            self.graphics_state.Tf = op.args  # agrs shally be [font, size]
        else:
            # ToDo: what commands we need to implement?
            # Need to support graphical states related to images transformations
            pass

    def is_operator(self, obj):
        return isinstance(obj, Token) and obj[0] not in '/01234567890+-.<[('

    def null_false_true_token(self):
        val = self.token()
        if val == 'null':
            val = null
        elif val == 'true':
            val = True
        elif val == 'false':
            val = False
        return val

    def _get_parser(self):
        if self.current in b'nft':
            # work around tokens which starts the same as null, false, true
            method = self.null_false_true_token
        else:
            method = super(ContentParser, self)._get_parser()
        if method is None:
            # assume token
            method = self.token
            # parse known content objects as objects rather than just tokens
            val = method()
            for i in range(len(val)):
                self.prev()
            if val == 'BT':
                method = self.bt_et
            elif val == 'BI':
                method = self.bi_ei
        return method

    def bt_et(self):
        """ returns TextObject """
        p = TextParser(self, self.buffer)
        return p.text_object()

    def bi_ei(self):
        """ returns InlineImage """
        p = InlineImageParser(self, self.buffer)
        return p.inline_image()
