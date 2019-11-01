from .base import BasicTypesParser
from .inlineimage import InlineImageParser
from .text import TextParser


class ContentParser(BasicTypesParser):
    """ Page.Content parser """

    def __init__(self, context, *args, **kwargs):
        self.context = context
        super(ContentParser, self).__init__(*args, **kwargs)

    def objects(self):
        """ Returns list of content objects as they follow in the document """
        res = []
        while self.current:
            self.maybe_spaces_or_comments()
            obj = self.object()
            res.append(obj)
            self.maybe_spaces_or_comments()
        return res

    def _get_parser(self):
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
        p = TextParser(self.context.fonts, self.fileobj, offset=self.last_block_offset + self.index)
        return p.text_object()

    def bi_ei(self):
        """ returns InlineImage """
        p = InlineImageParser(self.fileobj, offset=self.last_block_offset + self.index)
        return p.inline_image()
