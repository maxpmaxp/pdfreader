from copy import copy

from .types import Stream, Array, Dictionary


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
        super(StreamBasedObject, self).__init__(copy(stream.dictionary), copy(stream.stream))
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
        self._cache[item] = obj
        return self.doc.build(obj, lazy=True)


class DictBasedObject(Dictionary):
    """ Dictionary-based object. Can solve indirect references """

    def __init__(self, doc, *args, **kwargs):
        super(DictBasedObject, self).__init__(*args, **kwargs)
        self.doc = doc
        self._cache = dict()

    def __getattr__(self, item):
       return self[item]

    def __getitem__(self, item):
        if item in self._cache:
            return self._cache[item]
        obj = super(DictBasedObject, self).__getitem__(item)
        self._cache[item] = self.doc.build(obj, lazy=True)
        return self._cache[item]


def obj_factory(doc, obj):
    if isinstance(obj, Stream):
        if obj.Type == 'XObject':
            klass = XOBJECTS.get(obj.SubType, XObject)
        else:
            klass = STREAM_BASED_OBJECTS.get(obj.Type, StreamBasedObject)
    elif isinstance(obj, Dictionary):
        klass = DICT_OBJECTS.get(obj.get('Type'), DictBasedObject)
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

    def gen_pages(self, node=None):
        if node is None:
            node = self
        for child in node.Kids:
            if isinstance(child, Page):
                yield Page
            else:
                for page in self.gen_pages(child):
                    yield page


class Page(DictBasedObject):
    """ Type = Page
    """

    def gen_content(self):
        if isinstance(self.Contents, StreamBasedObject):
            yield self.Contents
        else:
            for c in self.Contents:
                yield c


class XObject(StreamBasedObject):
    """ Type = XObject
    """
    pass


class CMap(StreamBasedObject):
    """ Type = CMap
    """


class Metadata(StreamBasedObject):
    """ Type = Metadata
        Subtype = XML
    """

class Image(XObject):
    """ Type = XObject
        Subtype = Image
    """


class Form(XObject):
    """ Type = XObject
        Subtype = Form
    """


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
