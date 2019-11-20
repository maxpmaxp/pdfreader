class SimpleCanvas(object):
    images = None  # Shall be list of Image XObjects displayed with *do* command
    forms = None   # Shall be list of Form XObjects displayed with *do* command
    content = None          # Shall be a meaningful string representation of page content for further usage
    strings = None          # Shall be al list of decoded strings, no PDF commands
    inline_images = None    # Shall be list of InlineImage objects

    def __init__(self):
        self.reset()

    def reset(self):
        self.images = dict()
        self.forms = dict()
        self.content = ""
        self.inline_images = []
        self.strings = []