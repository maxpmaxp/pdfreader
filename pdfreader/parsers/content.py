import logging
log = logging.getLogger(__name__)

from .base import BasicTypesParser
from ..types.content import Operator, InlineImage
from ..types.native import null, Token
from .inlineimage import InlineImageParser


class ContentParser(BasicTypesParser):
    """ Page.Content parser

        Generates page stream objects:
        - Commands with operands, which are native PDF types (bool, Decimal, String etc.)
        - Inline images

    """

    indirect_references_allowed = False

    def objects(self):
        """ Returns list of content objects as they follow in the document """
        operands = []
        self.maybe_spaces_or_comments()
        while self.current:
            obj = self.object()
            if isinstance(obj, InlineImage):
                if operands:
                    log.debug("Skipping heading operands for inline image: {}".format(operands))
                operands = []
                yield obj
            elif self.is_operator(obj):
                op = Operator(obj, operands)
                yield op
                operands = []
            else:
                operands.append(obj)
            self.maybe_spaces_or_comments()
        if operands:
            log.debug("Skipping trailing operands at the end of stream: {}".format(operands))

    @staticmethod
    def is_operator(obj):
        """
        >>> ContentParser.is_operator(Token("Tj"))
        True
        >>> ContentParser.is_operator(Token("T*"))
        True
        >>> ContentParser.is_operator(Token("'"))
        True
        >>> ContentParser.is_operator(Token('"'))
        True
        >>> ContentParser.is_operator(Token('1rna'))
        False
        """
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
            if val == 'BI':
                method = self.bi_ei
        return method

    def bi_ei(self):
        """ returns InlineImage """
        p = InlineImageParser(self.buffer)
        return p.inline_image()
