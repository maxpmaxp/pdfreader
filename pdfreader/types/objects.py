from ..codecs.decoder import Decoder
from ..utils import cached_property
from .content import TextObject, InlineImage
from .native import Stream, Dictionary, Array, Name


class StartXRef(object):
    """ startxref
        123

        Pseudo object. Can be between indirect objects if any incremental updates.
    """

    def __init__(self, offset):
        self.offset = offset

    def __repr__(self):
        return "<StartXRef: {}>".format(self.offset)

    def __eq__(self, other):
        return self.offset == other.offset


class Trailer(object):
    """ trailer
            <<< ... .>>
        endtrailer

        Pseudo object. Can be between indirect objects if any incremental updates.
        """
    def __init__(self, params):
        self.params = params

    def __repr__(self):
        return "<Trailer: {}>".format(self.params)

    def __eq__(self, other):
        return self.params == other.params


class StreamBasedObject(Stream):
    """ Stream-based object. Can solve indirect references """

    def __init__(self, doc, stream):
        super(StreamBasedObject, self).__init__(stream.dictionary, stream.stream)
        self.doc = doc
        self._cache = dict()

    @classmethod
    def from_stream(cls, other):
        obj = super(StreamBasedObject, StreamBasedObject).from_stream(other)
        obj.doc = other.doc

    def __getattr__(self, item):
        if item in self._cache:
            return self._cache[item]
        obj = super(StreamBasedObject, self).__getattr__(item)
        obj = self.doc.build(obj, lazy=True)
        if (isinstance(obj, StreamBasedObject) and not obj.dictionary.get("Type"))\
            or (isinstance(obj, DictBasedObject) and not obj.get("Type")):
                hook = super(StreamBasedObject, self).__getattr__('_type__{}'.format(item))
                if hook and callable(hook):
                    obj = hook(obj)
        self._cache[item] = obj
        return self._cache[item]


class ArrayBasedObject(Array):
    """ Array-based object. Can solve indirect references """

    def __init__(self, doc, lst):
        self.doc = doc
        # ToDo: this must be lazier thing.
        # Need to build objects only on access attempte like a.index, a[i], a[1:2] etc.
        lst = [self.doc.build(obj, lazy=True) for obj in lst]
        super(ArrayBasedObject, self).__init__(lst)


class DictBasedObject(Dictionary):
    """ Dictionary-based object. Can solve indirect references """

    def __init__(self, doc, *args, **kwargs):
        super(DictBasedObject, self).__init__(*args, **kwargs)
        self.doc = doc
        self._cache = dict()

    def __getattr__(self, item):
        if item in self:
            return self[item]
        raise AttributeError(item)

    def __getitem__(self, item):
        if item in self._cache:
            return self._cache[item]
        obj = super(DictBasedObject, self).__getitem__(item)
        obj = self.doc.build(obj, lazy=True)
        if (isinstance(obj, StreamBasedObject) and not obj.dictionary.get("Type"))\
            or (isinstance(obj, DictBasedObject) and not obj.get("Type")):
                hook = getattr(self, '_type__{}'.format(item), None)
                if hook and callable(hook):
                    obj = hook(obj)
        self._cache[item] = obj
        return self._cache[item]

    def __delitem__(self, item): # real signature unknown
        """ Delete self[key]. """
        del self._cache[item]

    def get(self, item, default=None):
        try:
            val = self[item]
        except KeyError:
            val = default
        return val


def obj_factory(doc, obj):
    if isinstance(obj, Stream):
        if obj.Type == 'XObject':
            klass = XOBJECTS.get(obj.Subtype, XObject)
        else:
            klass = STREAM_BASED_OBJECTS.get(obj.Type, StreamBasedObject)
    elif isinstance(obj, Dictionary):
        klass = DICT_OBJECTS.get(obj.get('Type'), DictBasedObject)
    elif isinstance(obj, list):
        klass = ArrayBasedObject
    else:
        raise TypeError("Unsupported object type: {}".format(type(obj)))
    return klass(doc, obj)
        

class ObjectStream(StreamBasedObject):
    """ Type = ObjStm
    """
    pass


class Catalog(DictBasedObject):
    """ Type = Catalog
    """
    pass


class PageTreeNode(DictBasedObject):
    """ Type = Pages
    """

    def pages(self, node=None):
        if node is None:
            node = self
        for child in node.Kids:
            if isinstance(child, Page):
                yield child
            else:
                for page in self.pages(child):
                    yield page


class PageContentMixin(object):

    @cached_property
    def fonts(self):
        return self.Resources.get("Font", dict())

    @cached_property
    def decoders(self):
        return {name: Decoder(self.fonts[name]) for name in self.fonts.keys()}

    def text_objects(self):
        from ..parsers.content import ContentParser
        p = ContentParser(self, self.stream_content)
        for obj in p.objects():
            if isinstance(obj, TextObject):
                yield obj

    def inline_images(self):
        from ..parsers.content import ContentParser
        p = ContentParser(self, self.stream_content)
        for obj in p.objects():
            if isinstance(obj, InlineImage):
                yield obj

    def text(self, glue=""):
        return glue.join([to.to_string(glue) for to in self.text_objects()])

    def text_sources(self, glue="\n"):
        return glue.join([to.source for to in self.text_objects()])


class Page(PageContentMixin, DictBasedObject):
    """ Type = Page
    """

    @cached_property
    def stream_content(self):
        """ ToDo: Can BT instruction come in one content stream and have enclosing ET in a following one??
        """
        if isinstance(self.Contents, StreamBasedObject):
            res = self.Contents.filtered
        else:
            res = b''.join([ct.filtered for ct in self.Contents])
        return res


class XObject(StreamBasedObject):
    """ Type = XObject
    """
    pass


class CMap(StreamBasedObject):
    """ Type = CMap
    """
    def __init__(self, *args, **kwargs):
        super(CMap, self).__init__(*args, **kwargs)
        from ..parsers.cmap import CMapParser
        self.resource = CMapParser(self.filtered).cmap()


class Metadata(StreamBasedObject):
    """ Type = Metadata
        Subtype = XML
    """


class Image(XObject):
    """ Type = XObject
        Subtype = Image
    """


class Form(PageContentMixin, XObject):
    """ Type = XObject
        Subtype = Form
    """

    stream_content = XObject.filtered


class Group(XObject):
    """ Type = XObject
        Subtype = Group
    """


class OCG(DictBasedObject):
    """ Type = OCG
        Optional Content Group
    """


class OCMD(DictBasedObject):
    """ Type = OCMD
        Optional Content Membership Directory
    """


class Font(DictBasedObject):
    """ Type = Font
    """

    def _type__ToUnicode(self, obj):
        return CMap(obj.doc, obj)

    def _type__Encoding(self, obj):
        if isinstance(obj, (Name, Encoding)):
            val = obj
        else:
            val = Encoding(obj.doc, obj)
        return val


class Encoding(DictBasedObject):
    """ Type = Encoding
    """


class CIDFont(DictBasedObject):
    """ Type = CIDFont
    """


class FontDescriptior(DictBasedObject):
    """ Type = FontDescriptior
    """


class Halftone(DictBasedObject):
    """ Type = Halftone
    """


class Outlines(DictBasedObject):
    """ Type = Outlines
    """


class Collection(DictBasedObject):
    """ Type = Collection
    """


class CollectionField(DictBasedObject):
    """ Type = CollectionField
    """


class CollectionSort(DictBasedObject):
    """ Type = CollectionSort
    """


class CollectionSchema(DictBasedObject):
    """ Type = CollectionSchema
    """


class PageLabel(DictBasedObject):
    """ Type = PageLabel
    """


class Bread(DictBasedObject):
    """ Type = Bread
    """


class Thread(DictBasedObject):
    """ Type = Thread
    """


class Trans(DictBasedObject):
    """ Type = Trans
    """


class NavNode(DictBasedObject):
    """ Type = NavNode
    """


class Annot(DictBasedObject):
    """ Type = Annot
    """


class Border(DictBasedObject):
    """ Type = Border
    """


class Action(DictBasedObject):
    """ Type = Action
    """


class Sig(DictBasedObject):
    """ Type = Sig
    """


class SigRef(DictBasedObject):
    """ Type = SigRef
    """


class TransformParams(DictBasedObject):
    """ Type = TransformParams
    """


class Requirement(DictBasedObject):
    """ Type = Requirement
    """


class ReqHandler(DictBasedObject):
    """ Type = ReqHandler
    """


class Rendition(DictBasedObject):
    """ Type = Rendition
    """


class MediaCriteria(DictBasedObject):
    """ Type = MediaCriteria
    """


class MinBitDepth(DictBasedObject):
    """ Type = MinBitDepth
    """


class MinScreenSize(DictBasedObject):
    """ Type = MinScreenSize
    """


class MediaClip(DictBasedObject):
    """ Type = MediaClip
    """


class MediaPermissions(DictBasedObject):
    """ Type = MediaPermissions
    """


class MediaDuration(DictBasedObject):
    """ Type = MediaDuration
    """


class MediaScreenParams(DictBasedObject):
    """ Type = MediaScreenParams
    """


class FWParams(DictBasedObject):
    """ Type = FWParams
    """


class MediaOffset(DictBasedObject):
    """ Type = MediaOffset
    """

class Timespan(DictBasedObject):
    """ Type = Timespan
    """


class MediaPlayers(DictBasedObject):
    """ Type = MediaPlayers
    """


class MediaPlayerInfo(DictBasedObject):
    """ Type = MediaPlayerInfo
    """


class SoftwareIdentifier(DictBasedObject):
    """ Type = SoftwareIdentifier
    """


class Sound(DictBasedObject):
    """ Type = Sound
    """


class SlideShow(DictBasedObject):
    """ Type = SlideShow
    """


class LastModified(DictBasedObject):
    """ Type = LastModified
    """


class StructTreeRoot(DictBasedObject):
    """ Type = StructTreeRoot
    """


class StructElem(DictBasedObject):
    """ Type = StructElem
    """


class MCR(DictBasedObject):
    """ Type = MCR
        Marked Content Reference
    """


class OBJR(DictBasedObject):
    """ Type = OBJR
        Object Reference
    """


STREAM_BASED_OBJECTS = {
    'ObjectStream': ObjectStream,
    'XObject': XObject,
    'CMap': CMap,
    'Metadata': Metadata
}

XOBJECTS = {'Image': Image,
            'Form': Form,
            'Group': Group} 

DICT_OBJECTS = {
    'Catalog': Catalog,
    'Pages': PageTreeNode,
    'Page': Page,
    'OCG': OCG,
    'OCMD': OCMD,
    'Font': Font,
    'Encoding': Encoding,
    'CIDFont': CIDFont,
    'FontDescriptior': FontDescriptior,
    'Halftone': Halftone,
    'Outlines': Outlines,
    'Collection': Collection,
    'CollectionField': CollectionField,
    'CollectionSort': CollectionSort,
    'CollectionSchema': CollectionSchema,
    'PageLabel': PageLabel,
    'Bread': Bread,
    'Thread': Thread,
    'Trans': Trans,
    'NavNode': NavNode,
    'Annot': Annot,
    'Border': Border,
    'Action': Action,
    'Sig': Sig,
    'SigRef': SigRef,
    'TransformParams': TransformParams,
    'Requirement': Requirement,
    'ReqHandler': ReqHandler,
    'Rendition': Rendition,
    'MediaCriteria': MediaCriteria,
    'MinBitDepth': MinBitDepth,
    'MinScreenSize': MinScreenSize,
    'MediaClip': MediaClip,
    'MediaPermissions': MediaPermissions,
    'MediaDuration': MediaDuration,
    'MediaScreenParams': MediaScreenParams,
    'FWParams': FWParams,
    'MediaOffset': MediaOffset,
    'Timespan': Timespan,
    'MediaPlayers': MediaPlayers,
    'MediaPlayerInfo': MediaPlayerInfo,
    'SoftwareIdentifier': SoftwareIdentifier,
    'Sound': Sound,
    'SlideShow': SlideShow,
    'LastModified': LastModified,
    'StructTreeRoot': StructTreeRoot,
    'StructElem': StructElem,
    'MCR': MCR,
    'OBJR': OBJR
}
