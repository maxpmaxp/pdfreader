from itertools import islice
from ..document import PDFDocument


class Interpreter(object):

    parser_class = None
    operator_flow = ('before', 'on', 'after')

    def __init__(self, doc):
        self.doc = doc
        self.current_page_number = None
        self.canvas = None
        self._pages = dict()
        self.on_load()

    def on_load(self):
        self.navigate_page(1)

    @property
    def current_page(self):
        return self.navigate_page(self.current_page)

    @classmethod
    def from_fileobj(cls, fobj):
        doc = PDFDocument(fobj)
        return cls(doc)

    def navigate_page(self, n):
        if n not in self._pages:
            self._pages[n] = islice(self.doc.pages(), self.current_page - 1, self.current_page)
        return self._pages[n]

    def next_page(self):
        return self.navigate_page(self.current_page + 1)

    def prev_page(self):
        return self.navigate_page(self.current_page - 1)

    def clear_canvas(self):
        raise NotImplemented

    def get_stream(self):
        raise NotImplementedError

    def get_handler(self, op, stage):
        name = "{stage}_{op.name}".format(op=op, stage=stage)
        handler = getattr(self, name, None)
        if handler and callable(handler):
            return handler

    def notify(self, op):
        for stage in self.operator_flow:
            handler = self.get_handler(op, stage)
            if handler:
                handler(op)

    def render(self):
        self.clear_canvas()
        stream = self.get_stream()
        parser = self.parser_class(stream)
        for op in parser.objects():
            self.notify(op)
        return self.canvas
