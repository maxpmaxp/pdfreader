class SimpleCanvas(object):
    """ Very simple canvas for PDF viewer: can contain page images (inline and XObject),
        strings, forms and text content.
    """

    #: Shall be list of :class:`~pdfreader.types.objects.Image` XObjects rendered with *do* command
    images = None

    #: Shall be list of :class:`~pdfreader.types.objects.Form` XObjects displayed with *do* command
    forms = None

    #: Shall be a meaningful string representation of page content for further usage (decoded strings + markdown for example)
    text_content = None

    #: Shall be al list of decoded strings, no PDF commands
    strings = None

    #: Shall be list of :class:`~pdfreader.types.content.InlineImage` objects page stream contains
    inline_images = None

    def __init__(self):
        self.reset()

    def reset(self):
        self.images = dict()
        self.forms = dict()
        self.text_content = ""
        self.inline_images = []
        self.strings = []

