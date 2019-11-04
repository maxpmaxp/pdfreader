from .base import BasicTypesParser
from ..types.native import null
from .inlineimage import InlineImageParser
from .text import TextParser


class ContentParser(BasicTypesParser):
    """ Page.Content parser """

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super(ContentParser, self).__init__(*args, **kwargs)

    def objects(self):
        """ Returns list of content objects as they follow in the document """
        while self.current:
            self.maybe_spaces_or_comments()
            yield self.object()
            self.maybe_spaces_or_comments()

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
            # ToDo:  we need to parse different commands here one days
        return method

    def bt_et(self):
        """ returns TextObject """
        p = TextParser(self.context, self.buffer)
        return p.text_object()

    def bi_ei(self):
        """ returns InlineImage """
        p = InlineImageParser(self.buffer)
        return p.inline_image()
