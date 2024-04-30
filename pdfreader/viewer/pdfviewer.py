import logging
log = logging.getLogger(__name__)

from itertools import islice

from ..document import PDFDocument
from ..types.content import Operator, InlineImage
from ..types.objects import StreamBasedObject
from .graphicsstate import GraphicsStateStack, GraphicsState
from .resources import Resources


class PageDoesNotExist(ValueError):
    """ Exception. Supposed to be raised by PDF viewers on navigation to non-existing pages.  """
    pass


class CanvasIterator(object):
    """ Iterator of canvases for all pages """

    def __init__(self, viewer):
        self.viewer = viewer
        self.last_page_reached = False

    def __next__(self):
        if self.last_page_reached:
            raise StopIteration()
        self.viewer.render()
        canvas = self.viewer.canvas.copy()
        try:
            self.viewer.next()
        except PageDoesNotExist:
            self.last_page_reached = True
        return canvas


class PagesIterator(object):
    """ Iterator of document pages """

    def __init__(self, viewer):
        self.viewer = viewer
        self.last_page_reached = False

    def __next__(self):
        if self.last_page_reached:
            raise StopIteration()
        page = self.viewer.current_page
        try:
            self.viewer.next()
        except PageDoesNotExist:
            self.last_page_reached = True
        return page


class ContextualViewer(object):
    """ PDF viewer that operates with predefined context: bytes stream, resources and graphical state stack """
    parser_class = None
    operator_flow = ('before', 'on', 'after')
    canvas_class = None
    graphics_state_stack_class = GraphicsStateStack

    # custom Operator.name to handler name mapping to handle non-pythonic names like T*
    # for example:
    #
    # operators_aliases = {'T*': 'Tstar'}
    #
    # def on_Tstar(self, op):
    #     ...

    operators_aliases = {}

    def __init__(self, stream, resources, gss):
        self.canvas = self.canvas_class()
        self.gss = gss
        self.resources = resources
        self.stream = stream
        self.on_document_load()

    def get_handler_name(self, obj, stage):
        name = stage
        if isinstance(obj, Operator):
            opname = self.operators_aliases.get(obj.name, obj.name)
            name = "{stage}_{opname}".format(opname=opname, stage=stage)
        elif isinstance(obj, InlineImage):
            name = "{stage}_inline_image".format(stage=stage)
        else:
            log.debug("Unexpected content object type {}".format(type(obj)))
        return name

    def get_resources(self):
        return self.resources

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
        """ Renders current page onto current canvas by interpreting content stream(s) commands.
            Charnges: graphical state, canvas.
        """
        parser = self.parser_class(self.stream)
        for obj in parser.objects():
            self.notify(obj)

    # Events

    def on_document_load(self):
        pass


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
        self.gss.state.CTM = obj.args  # supposed to be an array

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
        self.gss.state.D = obj.args  # supposed to be an array

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
            self.gss.state.update(GraphicsState(**state))
        else:
            log.debug("Graphics state {} was not found on resources".format(name))

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


class PDFViewer(ContextualViewer):
    """ PDF document viewer and navigator  """

    operators_aliases = {}

    def __init__(self, fobj, password=''):
        """ Constructor method """
        self._pages = {}  # pages cache
        self.current_page_number = None
        self.doc = PDFDocument(fobj, password=password)
        super(PDFViewer, self).__init__(None, Resources(), self.graphics_state_stack_class())

    @property
    def metadata(self):
        """
        Returns document metadata from file's trailer info dict

        :return: dict, if metadata exists `None` otherwise.
        """
        return self.doc.metadata

    @property
    def current_page(self):
        """ :return: Current :class:`~pdfreader.types.objects.Page` instance """
        return self._pages[self.current_page_number]

    def navigate(self, n):
        """
        Navigates viewer to n-th page of the document.
        Side-effects: clears canvas, resets page resources, resets graphics state

        :param n: page number. The very first page has number 1

        :raises PageDoesNotExist: if there is no n-th page

        """
        if n not in self._pages:
            try:
                self._pages[n] = next(islice(self.doc.pages(), n - 1, n))
            except StopIteration:
                raise PageDoesNotExist(n)
        self.before_navigate(n)
        self.current_page_number = n
        self.after_navigate(n)

    def next(self):
        """
        Navigates viewer to the next page of the document.
        Side-effects: clears canvas, resets page resources, resets graphics state

        :raises PageDoesNotExist: if there is no next page

        """
        self.navigate(self.current_page_number + 1)

    def __iter__(self):
        """
        Returns document's canvas iterator.
        """
        return CanvasIterator(self)

    def iter_pages(self):
        """
        Returns document's pages iterator.
        """
        return PagesIterator(self)

    def prev(self):
        """
        Navigates viewer to the previous page of the document.
        Side-effects: clears canvas, resets page resources, resets graphics state

        :raises PageDoesNotExist: if there is no previous page
        """
        self.navigate(self.current_page_number - 1)

    def get_handler_name(self, obj, stage):
        name = stage
        if isinstance(obj, Operator):
            opname = self.operators_aliases.get(obj.name, obj.name)
            name = "{stage}_{opname}".format(opname=opname, stage=stage)
        elif isinstance(obj, InlineImage):
            name = "{stage}_inline_image".format(stage=stage)
        else:
            log.debug("Unexpected content object type {}".format(type(obj)))
        return name

    def get_resources(self):
        return Resources.from_page(self.current_page)

    # Events

    def on_document_load(self):
        super(PDFViewer, self).on_document_load()
        self.current_page_number = 1
        self.navigate(self.current_page_number)

    def before_navigate(self, n):
        pass

    def after_navigate(self, n):
        self.canvas.reset()
        self.gss = GraphicsStateStack()
        self.resources = self.get_resources()

        # get content stream
        if isinstance(self.current_page.Contents, StreamBasedObject):
            self.stream = self.current_page.Contents.filtered
        else:
            # Join array of streams
            self.stream = b''.join([ct.filtered for ct in self.current_page.Contents])

    @property
    def annotations(self):
        """
        Current page annotations

        :getter: Returns list of annotations for current page
        :type: string
        """
        return self.current_page.Annots
