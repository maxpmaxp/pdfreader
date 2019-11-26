pdfreader.types submodule
==========================

 .. autoclass:: pdfreader.types.objects.DictBasedObject

 .. autoclass:: pdfreader.types.objects.StreamBasedObject

    .. autoproperty:: filtered

 .. autoclass:: pdfreader.types.objects.ArrayBasedObject

 .. autoclass:: pdfreader.types.objects.Catalog

 .. autoclass:: pdfreader.types.objects.PageTreeNode

    .. automethod:: pages

 .. autoclass:: pdfreader.types.objects.Page

 .. autoclass:: pdfreader.types.objects.Image

    .. autoproperty:: filtered
    .. automethod:: to_Pillow


 .. autoclass:: pdfreader.types.objects.Form

    .. autoproperty:: filtered

 .. autoclass:: pdfreader.types.objects.XObject

    .. autoproperty:: filtered

 .. autoclass:: pdfreader.types.content.InlineImage

    .. autoattribute:: dictionary
      :annotation:
    .. autoattribute:: data
      :annotation:
    .. autoproperty:: filtered
    .. automethod:: to_Pillow

 .. autoclass:: pdfreader.types.content.Operator

    .. autoattribute:: name
      :annotation:
    .. autoattribute:: args
      :annotation:
