from ..exceptions import ParserException
from ..types.native import Name, Token
from ..types.cmap import CodespaceRanges, MappedCodespaceRanges, CMapResource
from .base import BasicTypesParser


class CMapParser(BasicTypesParser):
    """ Very poor implementation as we don't support PostScript language in full """

    def object_or_token(self):
        state = self.get_state()

        try:
            obj = super(CMapParser, self).object()
        except ParserException:
            self.set_state(state)
            obj = self.token()
        return obj

    def skip_until_name(self, name):
        while True:
            self.maybe_spaces_or_comments()
            if self.current is None:
                break
            obj = self.object_or_token()
            if isinstance(obj, Name) and obj == name:
                for _ in range(len(name) + 1): # as name contains leading /
                    self.prev()
                return True
        return False

    def skip_until_token(self, name):
        while True:
            if self.current is None:
                break
            self.maybe_spaces_or_comments()
            if self.current is None:
                break
            obj = self.object_or_token()
            if isinstance(obj, Token) and obj == name:
                for _ in range(len(name)):
                    self.prev()
                return True
        return False

    def cmap_name(self):
        self.skip_until_name('CMapName')
        self.expected_name('CMapName')
        self.maybe_spaces_or_comments()
        return self.name()

    def cmap(self):
        """
        >>> import pkg_resources
        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-sample.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        '83pv-RKSJ-H'
        >>> cmap.codespace_ranges
        <CodespaceRanges:ranges=[<Range:0-128>, <Range:33088-40956>, <Range:160-22 ...>
        >>> cmap.cid_ranges
        <MappedCodespaceRanges:ranges=[<MapRange:32-126,1>, <MapRange:128-128,97>, <MapR ...>
        >>> len(cmap.cid_ranges.ranges)
        222
        >>> cmap.notdef_ranges
        <MappedCodespaceRanges:ranges=[<MapRange:0-31,1>]>
        >>> cmap.bf_ranges
        <MappedCodespaceRanges:ranges=[]>
        """
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

        # <n> dict begin
        self.non_negative_int()
        self.maybe_spaces_or_comments()
        self.expected_token('dict')
        self.maybe_spaces_or_comments()
        self.expected_token('begin')
        self.maybe_spaces_or_comments()

        # begincmap
        self.expected_token('begincmap')
        self.maybe_spaces_or_comments()
        state = self.get_state() # save parser state

        cmapname = self.cmap_name()

        # Extarct Coderanges
        self.set_state(state)
        codespaceranges = CodespaceRanges()
        while self.skip_until_token("begincodespacerange"):
            codespaceranges.merge(self.codespacerange())

        # Extarct CID mappings: range & chars
        self.set_state(state)
        cidranges = MappedCodespaceRanges()
        while self.skip_until_token("begincidrange"):
            cidranges.merge(self.mapped_codespacerange("cid"))
        self.set_state(state)
        while self.skip_until_token("begincidchar"):
            cidranges.merge(self.mapped_char("cid"))

        # Extracts NotDef mappings: range & chars
        self.set_state(state)
        notdefranges = MappedCodespaceRanges()
        while self.skip_until_token("beginnotdefrange"):
            notdefranges.merge(self.mapped_codespacerange("notdef"))
        self.set_state(state)
        while self.skip_until_token("beginnotdefchar"):
            notdefranges.merge(self.mapped_char("notdef"))

        # Extracts BF mappings: range & chars
        self.set_state(state)
        bfranges = MappedCodespaceRanges()
        while self.skip_until_token("beginbfrange"):
            bfranges.merge(self.mapped_codespacerange("bf"))
        self.set_state(state)
        while self.skip_until_token("beginbfchar"):
            bfranges.merge(self.mapped_char("bf"))

        return CMapResource(cmapname,
                            codespace_ranges=codespaceranges,
                            cid_ranges=cidranges,
                            notdef_ranges=notdefranges,
                            bf_ranges=bfranges)

    def codespacerange(self):
        self.expected_token("begincodespacerange")
        self.maybe_spaces_or_comments()
        res = CodespaceRanges()
        while self.current == b"<":
            cr_from = self.hexstring()
            self.maybe_spaces_or_comments()
            cr_to = self.hexstring()
            self.maybe_spaces_or_comments()
            res.add(cr_from, cr_to)
        self.expected_token("endcodespacerange")
        return res

    def mapped_codespacerange(self, rangename):
        self.expected_token("begin{}range".format(rangename))
        self.maybe_spaces_or_comments()
        res = MappedCodespaceRanges()
        while self.current == b"<":
            cr_from = self.hexstring()
            self.maybe_spaces_or_comments()
            cr_to = self.hexstring()
            self.maybe_spaces_or_comments()
            cid_from = self.non_negative_int()
            self.maybe_spaces_or_comments()
            res.add(cr_from, cr_to, cid_from)
        self.expected_token("end{}range".format(rangename))
        return res

    def mapped_char(self, rangename):
        self.expected_token("begin{}char".format(rangename))
        self.maybe_spaces_or_comments()
        res = MappedCodespaceRanges()
        while self.current == b"<":
            src_code = self.hexstring()
            self.maybe_spaces_or_comments()
            dst_code = self.hexstring()
            self.maybe_spaces_or_comments()
            res.add(src_code, src_code, dst_code)
        self.expected_token("end{}char".format(rangename))
        return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
