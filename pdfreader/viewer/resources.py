import logging

from ..types.native import Dictionary, Array
from ..types.objects import Page


class Resources(object):
    """ Page resources. See 7.8.3 resources Dict """
    _fields = ('ExtGState', 'ColorSpace', 'Pattern', 'Shading', 'XObject', 'Font', 'ProcSet')

    def __init__(self, **kwargs):
        self.ExtGState = kwargs.get('ExtGState') or dict()
        self.ColorSpace = kwargs.get('ColorSpace') or dict()
        self.Pattern = kwargs.get('Pattern') or dict()
        self.Shading = kwargs.get('Shading') or dict()
        self.XObject = kwargs.get('XObject') or dict()
        self.Font = kwargs.get('Font') or dict()
        self.ProcSet = kwargs.get('ProcSet') or set() # supposed to be a set predefined procedures names
        self.Properties = kwargs.get('Properties') or dict()

    @classmethod
    def from_page(cls, page: Page):
        """ Creates Resources object from Page instance """

        resources_stack = []
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
        kwargs = dict()
        while resources_stack:
            res = resources_stack.pop()
            for entry, dict_or_array in res.items():
                if not dict_or_array:
                    continue

                if isinstance(dict_or_array, Dictionary):
                    if entry not in kwargs:
                        kwargs[entry] = dict()
                    for k, v in dict_or_array.items():
                        kwargs[entry][k] = v
                elif isinstance(dict_or_array, Array):
                    if entry not in kwargs:
                        kwargs[entry] = set()
                    kwargs[entry].update(dict_or_array)
                else:
                    logging.warning("Skipping unexpected resources entry type: {} -> {}"
                                    .format(entry, type(dict_or_array)))

        return Resources(**kwargs)
