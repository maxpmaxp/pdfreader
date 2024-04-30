import logging
log = logging.getLogger(__name__)

from ..types.native import Dictionary, Array, Name
from ..types.objects import Page


class Resources(object):
    """ Page resources.
        See `sec 7.8.3 Resource Dictionaries <https://opensource.adobe.com/dc-acrobat-sdk-docs/standards/pdfstandards/pdf/PDF32000_2008.pdf#page=82>`_ """
    _fields = ('ExtGState', 'ColorSpace', 'Pattern', 'Shading', 'XObject', 'Font', 'ProcSet', 'Properties')

    def __init__(self, **kwargs):
        self.ExtGState = kwargs.get('ExtGState') or {}
        self.ColorSpace = kwargs.get('ColorSpace') or {}
        self.Pattern = kwargs.get('Pattern') or {}
        self.Shading = kwargs.get('Shading') or {}
        self.XObject = kwargs.get('XObject') or {}
        self.Font = kwargs.get('Font') or {}
        self.ProcSet = kwargs.get('ProcSet') or set() # supposed to be a set predefined procedures names
        self.Properties = kwargs.get('Properties') or {}

    @classmethod
    def from_page(cls, page: Page, resources_stack=None):
        """ Creates Resources object from Page instance """

        resources_stack = resources_stack or []
        # get current page resources
        node = page
        if node.Resources:
            resources_stack.append(node.Resources)

        # get parent pages tree nodes (Pages objects)
        while node.Parent:
            node = node.Parent
            if node.Resources:
                resources_stack.append(node.Resources)

        # build resources inheriting from parents if missing
        kwargs = {}
        while resources_stack:
            res = resources_stack.pop()
            for entry, dict_or_array in res.items():
                if not dict_or_array:
                    continue

                if isinstance(dict_or_array, Dictionary):
                    if entry not in kwargs:
                        kwargs[entry] = {}
                    for k, v in dict_or_array.items():
                        kwargs[entry][k] = v
                elif isinstance(dict_or_array, Array):
                    if entry not in kwargs:
                        kwargs[entry] = set()
                    for pname in dict_or_array:
                        if isinstance(pname, Name):
                            kwargs[entry].add(pname)
                        else:
                            kwargs[entry].update(pname)
                else:
                    log.debug("Skipping unexpected resources entry type: {} -> {}"
                              .format(entry, type(dict_or_array)))

        return Resources(**kwargs)
