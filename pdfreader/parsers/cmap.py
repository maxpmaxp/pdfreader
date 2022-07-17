import logging
log = logging.getLogger(__name__)

from ..exceptions import ParserException
from ..types.native import Name, Token, Integer, HexString, Array
from ..types.cmap import CodespaceRanges, MappedCodespaceRanges, CMapResource, Range, MapRange, BFChar
from .base import BasicTypesParser


class CMapParserException(ParserException):
    pass


class CMapParser(BasicTypesParser):
    """ Very poor implementation as we don't support PostScript language in full """

    exception_class = CMapParserException
    indirect_references_allowed = False

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

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-sample-missing-name.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name is None
        True
        >>> len(cmap.bf_ranges.ranges)
        7
        >>> cmap.bf_ranges['01']
        ' '

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-empty-name.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        ''
        >>> len(cmap.bf_ranges.ranges)
        1

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-sample-3.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        'Adobe-Identity-UCS'
        >>> len(cmap.bf_ranges.ranges)
        64
        >>> cmap.codespace_ranges
        <CodespaceRanges:ranges=[<Range:0000-FFFF>]>

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-sample.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        '83pv-RKSJ-H'
        >>> cmap.codespace_ranges
        <CodespaceRanges:ranges=[<Range:00-80>, <Range:8140-9FFC>, <Range:A0-DF>,  ...>
        >>> cmap.cid_ranges
        <MappedCodespaceRanges:ranges=[<MapRange:20-7E,1>, <MapRange:80-80,97>, <MapRang ...>
        >>> len(cmap.cid_ranges.ranges)
        222
        >>> cmap.notdef_ranges
        <MappedCodespaceRanges:ranges=[<MapRange:00-1F,1>]>
        >>> cmap.bf_ranges
        <MappedCodespaceRanges:ranges=[]>

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-sample-2.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        'Adobe-Identity-UCS'
        >>> len(cmap.bf_ranges.ranges)
        69

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-sample-bfrange-with-list.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        'Adobe-Identity-UCS'
        >>> len(cmap.bf_ranges.ranges)
        70
        >>> cmap.bf_ranges['0001']
        ' '
        >>> cmap.bf_ranges['0002']
        'U'
        >>> cmap.bf_ranges['0045']
        '6'

        >>> fd = pkg_resources.resource_stream('pdfreader.parsers', 'cmap-samples/cmap-sample-bfrange-with-list.txt')
        >>> cmap = CMapParser(fd).cmap()
        >>> cmap.name
        'Adobe-Identity-UCS'
        >>> len(cmap.bf_ranges.ranges)
        70
        >>> cmap.bf_ranges['0001']
        ' '
        >>> cmap.bf_ranges['0002']
        'U'
        >>> cmap.bf_ranges['0045']
        '6'

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

        try:
            cmapname = self.cmap_name()
        except ParserException:
            # see cmap-sample-4.txt (page 9 samples/tyler-or-inline-image.pdf) - missing /CMapName
            log.debug("Missing /CMapName")
            cmapname = None
            self.set_state(state)

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
            res.add(Range(cr_from, cr_to))
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
            cid_from = self.object()
            if not isinstance(cid_from, (HexString, Integer, Array)):
                self.on_parser_error("Int, Hexstring or Array expected")
            if isinstance(cid_from, (Integer, HexString)):
                res.add(MapRange(cr_from, cr_to, cid_from))
            else:
                # mapping represented as an array
                for i, v in enumerate(Range(cr_from, cr_to)):
                    res.add(BFChar(v, cid_from[i]))
            self.maybe_spaces_or_comments()

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
            if rangename == 'bf':
                obj = BFChar(src_code, dst_code)
            else:
                obj = MapRange(src_code, src_code, dst_code)
            res.add(obj)
        self.expected_token("end{}char".format(rangename))
        return res


if __name__ == "__main__":
    import doctest
    doctest.testmod()
