pdfreader.types submodule
==========================

 .. autoclass:: pdfreader.types.objects.DictBasedObject

 .. autoclass:: pdfreader.types.objects.StreamBasedObject

 .. autoclass:: pdfreader.types.objects.ArrayBasedObject

 .. autoclass:: pdfreader.types.objects.Catalog

 .. autoclass:: pdfreader.types.objects.PageTreeNode

    .. automethod:: pages

 .. autoclass:: pdfreader.types.objects.Page

 .. autoclass:: pdfreader.types.objects.Image

    .. automethod:: to_Pillow


 .. autoclass:: pdfreader.types.objects.Form

 .. autoclass:: pdfreader.types.objects.XObject

 .. autoclass:: pdfreader.types.content.InlineImage

    .. autoattribute:: dictionary
    .. autoattribute:: data
    .. autoproperty:: filtered
    .. automethod:: to_Pillow

 .. autoclass:: pdfreader.types.content.Operator

    .. autoattribute:: name
    .. autoattribute:: args