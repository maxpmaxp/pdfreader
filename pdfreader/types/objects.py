from ..pillow import PILImageMixin
from .native import Stream, Dictionary, Array


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
    """ Stream-based object.
        Automatically resolves indirect references on attributes access """

    def __init__(self, doc, stream):
        super(StreamBasedObject, self).__init__(stream.dictionary, stream.stream)
        self.doc = doc
        self._cache = {}

    @classmethod
    def from_stream(cls, other):
        obj = super(StreamBasedObject, StreamBasedObject).from_stream(other)
        obj.doc = other.doc

    def __getattr__(self, item):
        if item in self._cache:
            return self._cache[item]
        obj = super(StreamBasedObject, self).__getattr__(item)
        obj = self.doc.build(obj, lazy=True)
        self._cache[item] = obj
        return self._cache[item]


class ArrayBasedObject(Array):
    """ Array-based object.
        Automatically resolves indirect references on items access """

    def __init__(self, doc, lst):
        self.doc = doc
        # ToDo: this must be lazier thing.
        # Need to build objects only on access attempt only. For example: a.index, a[i], a[1:2] etc.
        lst = [self.doc.build(obj, lazy=True) for obj in lst]
        super(ArrayBasedObject, self).__init__(lst)


class DictBasedObject(Dictionary):
    """ Dictionary-based object.
        Automatically resolves indirect references on attributes/items access """

    def __init__(self, doc, *args, **kwargs):
        super(DictBasedObject, self).__init__(*args, **kwargs)
        self.doc = doc
        self._cache = {}

    def __getattr__(self, item):
        return self.get(item)

    def __getitem__(self, item):
        if item in self._cache:
            return self._cache[item]
        obj = super(DictBasedObject, self).__getitem__(item)
        obj = self.doc.build(obj, lazy=True)
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

    # override defaults to build Dictionary values before returning

    def keys(self):
        return [k for k in super(DictBasedObject, self).keys()]

    def values(self):
        return [self[k] for k in super(DictBasedObject, self).keys()]

    def items(self):
        return [(k, self[k]) for k in super(DictBasedObject, self).keys()]

    def pop(self, i, **kwargs):
        if i in self:
            res = self[i]
            _ = super(DictBasedObject, self).pop(i)
        else:
            res = super(DictBasedObject, self).pop(i, **kwargs)
        return res

    def popitem(self):
        if not self:
            raise KeyError()
        k = next(iter(super(DictBasedObject, self).keys()))
        return k, self.pop(k)


def obj_factory(doc, obj):
    klass = None
    if isinstance(obj, Stream):
        if obj.Type == 'XObject':
            klass = XOBJECTS.get(obj.Subtype, XObject)
        else:
            klass = STREAM_BASED_OBJECTS.get(obj.Type, StreamBasedObject)
    elif isinstance(obj, Dictionary):
        klass = DICT_OBJECTS.get(obj.get('Type'), DictBasedObject)
    elif isinstance(obj, list):
        klass = ArrayBasedObject

    return klass(doc, obj) if klass else obj
        

class ObjectStream(StreamBasedObject):
    """ Type = ObjStm
    """
    pass


class Catalog(DictBasedObject):
    """
    Dictionary based object. (Type = Catalog)
    See PDF 1.7 specification `sec. 7.7.2 - DocumentCatalog <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=71>`_
    """
    pass


class PageTreeNode(DictBasedObject):
    """
        Dictionary based object. (Type = Pages)
        See PDF 1.7 specification `sec. 7.7.3.2 - Page Tree Nodes <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=76>`_
    """

    def pages(self, node=None):
        """
        Yields tree node pages one by one.

        :return:  :class:`~pdfreader.types.objects.Page` generator.
        """
        if node is None:
            node = self
        for child in node.Kids:
            if isinstance(child, Page):
                yield child
            else:
                for page in self.pages(child):
                    yield page


class Page(DictBasedObject):
    """
    Dictionary based Page object. (Type = Page)
    See PDF 1.7 specification `sec. 7.7.3.3 - Page Objects <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=77>`_
    """


class XObject(StreamBasedObject):
    """
    Stream based XObject object. (Type = XObject)
    See PDF 1.7 specification `sec. 8.8 - External Objects <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=201>`_
    """


class CMap(StreamBasedObject):
    """ Type = CMap
    """


class Metadata(StreamBasedObject):
    """ Type = Metadata
        Subtype = XML
    """


class Image(PILImageMixin, XObject):
    """
    Stream based XObject object. (Type = XObject, Subtype = Image)
    See PDF 1.7 specification `sec. 8.9 - Images <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=203>`_
    """


class Form(XObject):
    """
    Stream based XObject object. (Type = XObject, Subtype = Form)
    See PDF 1.7 specification `sec. 8.10 - Form XObjects <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=217>`_
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
