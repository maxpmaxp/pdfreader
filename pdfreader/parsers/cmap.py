from ..exceptions import ParserException
from ..types import Name, Token
from .base import BasicTypesParser


class CMapParser(BasicTypesParser):


    def object_or_token(self):
        try:
            obj = super(CMapParser, self).object()
        except ParserException:
            obj = self.token()
        return obj

    def skip_until_name(self, name):
        while True:
            self.maybe_spaces_or_comments()
            obj = self.object_or_token()
            if isinstance(obj, Name) and obj == name:
                for _ in range(len(name)):
                    self.prev()

    def skip_until_token(self, name):
        while True:
            self.maybe_spaces_or_comments()
            obj = self.object_or_token()
            if isinstance(obj, Token) and obj == name:
                for _ in range(len(name)):
                    self.prev()

    def cmap_name(self):
        self.skip_until_name('CMapName')
        self.maybe_spaces_or_comments()
        return self.name()

    def cmap(self):
        #/CIDInit /ProcSet findresource begin
        self.maybe_spaces_or_comments()
        self.expected_name('CIDInit')
        self.maybe_spaces_or_comments()
        self.expected_name('ProcSet')
        self.maybe_spaces_or_comments()
        self.expected_token("findresource")
        self.maybe_spaces_or_comments()
        self.expected_token("begin")
        self.maybe_spaces_or_comments()

        # 12 dict begin
        self.expected_numeric(12)
        self.maybe_spaces_or_comments()
        self.expected_token('dict')
        self.maybe_spaces_or_comments()
        self.expected_token('begin')

        # begincmap
        self.expected_token('begincmap')
        state = self.get_state() # save parser state

        cmap_name = self.cmap_name()
        self.set_state(state)

        # ToDO:
        # extract codespaceranges
        # extract notdefranges
        # extract cidranges
        # extract bfranges
        # extract bfchars

        # Class CMap - can decode a character
