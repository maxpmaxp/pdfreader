import logging

from itertools import islice

from ..document import PDFDocument
from ..types.content import Operator, InlineImage
from ..types.objects import StreamBasedObject
from .graphicsstate import GraphicsStateStack, GraphicsState
from .resources import Resources


class PDFViewer(object):

    parser_class = None
    operator_flow = ('before', 'on', 'after')
    canvas_class = None
    graphics_state_stack_class = GraphicsStateStack

    # custom Operator.name to handler name mapping to handle non-pythonic names like T*
    # for example:
    #
    # operators_to_handlers = {'T*': 'Tstar}
    #
    # def on_Tstar(self, op):
    #     ...

    operators_to_handlers = dict()

    def __init__(self, fobj):
        self._pages = dict()  # pages cache
        self.stream = None
        self.current_page_number = None
        self.doc = PDFDocument(fobj)
        self.canvas = self.canvas_class()
        self.gss = self.graphics_state_stack_class()
        self.resources = Resources()
        self.on_document_load()

    @property
    def current_page(self):
        return self._pages[self.current_page_number]

    def navigate(self, n):
        self.before_navigate(n)
        if n not in self._pages:
            self._pages[n] = next(islice(self.doc.pages(), n - 1, n))
        self.current_page_number = n
        self.after_navigate(n)

    def next(self):
        self.navigate(self.current_page_number + 1)

    def prev(self):
        self.navigate(self.current_page_number - 1)

    def get_handler_name(self, obj, stage):
        name = stage
        if isinstance(obj, Operator):
            name = "{stage}_{op.name}".format(op=obj, stage=stage)
        elif isinstance(obj, InlineImage):
            name = "{stage}_inline_image".format(stage=stage)
        else:
            logging.warning("Unexpected content object type {}".format(type(obj)))
        return name

    def notify(self, obj):
        """
        Handlers call order:
            1. before_handler(obj)

            2. Specific handlers calls:
              - InlineImage objects: before_inline_image -> on_inline_image -> after_inline_image
              - Operator objects:
                    * _before_<name>_ -> _on_<name>_ -> _after_<name>_

            3. after_handler(obj)
        """
        self.before_handler(obj)
        for stage in self.operator_flow:
            name = self.get_handler_name(obj, stage)
            if name:
                handler = getattr(self, name, None)
                if handler and callable(handler):
                    handler(obj)
        self.after_handler(obj)

    def render(self):
        parser = self.parser_class(self.stream)
        for obj in parser.objects():
            self.notify(obj)

    # Events

    def on_document_load(self):
        self.current_page_number = 1
        self.navigate(self.current_page_number)

    def before_navigate(self, n):
        pass

    def after_navigate(self, n):
        self.canvas.reset()
        self.gss = GraphicsStateStack()
        self.resources = Resources.from_page(self.current_page)

        # get content stream
        if isinstance(self.current_page.Contents, StreamBasedObject):
            self.stream = self.current_page.Contents.filtered
        else:
            # Join array of streams
            self.stream = b''.join([ct.filtered for ct in self.current_page.Contents])

    # default stream object handlers
    def before_handler(self, obj):
        pass

    def after_handler(self, obj):
        pass

    # Graphics State commands
    def on_q(self, obj):
        """ Save graphics state """
        self.gss.save_state()

    def on_Q(self, obj):
        """ Restore graphics state """
        self.gss.restore_state()

    def on_cm(self, obj):
        """ Modify current transformation matrix """
        self.gss.state.CTM = obj.args # supposed to be an array

    def on_w(self, obj):
        """ Modify current line width """
        self.gss.state.LW = obj.args[0]

    def on_J(self, obj):
        """ Set line cap style """
        self.gss.state.LC = obj.args[0]

    def on_j(self, obj):
        """ Set line join style """
        self.gss.state.LJ = obj.args[0]

    def on_M(self, obj):
        """ Set miter limit """
        self.gss.state.ML = obj.args[0]

    def on_d(self, obj):
        """ Set line dash pattern """
        self.gss.state.D = obj.args # supposed to be an array

    def on_ri(self, obj):
        """ Set color rendering intent """
        self.gss.state.RI = obj.args[0]

    def on_i(self, obj):
        """ Set flatness tolerance """
        self.gss.state.FL = obj.args[0]

    def on_gs(self, obj):
        """ Set graphics state from resources """
        name = obj.args[0]
        state = self.resources.ExtGState.get(name)
        if state:
            self.gss.state = GraphicsState(**state)
        else:
            logging.warning("Graphics state {} was not found on resources".format(name))

    # *Do* operator state manipulations
    def before_Do(self, op):
        self.gss.save_state()

    def after_Do(self, op):
        self.gss.restore_state()


    # Custom commands events shall be like
    #
    # def before_Tj(self, op):
    #     ...
    #
    # def on_Tj(self, op):
    #     ...
    #
    # def after_Tj(self, op):
    #     ...
    #
    # def on_BX(self, op):
    #     ...
    #
    # def on_EX(self, op):
    #     ...
    #