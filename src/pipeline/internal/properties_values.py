"""Manage the properties values that make properties work.

Those are the objects stored in some properties to extend behaviours.
"""

from python_core.types import dictionaries


class DictionaryValue(dictionaries.Dictionary):
    """Manage the dictionaries in the properties."""

    parent = None

    def __getattribute__(self, name):
        """Get an attribute from the value or its parent property.

        Arguments:
            name (str): The name of the attribute or property.

        Returns:
            -: The attribute.
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self.parent, name)


class PropertiesDictionaryValue(DictionaryValue):
    """Manage a dictionary that stores properties."""

    def __getitem__(self, name):
        """Get a child property stored in the current dictionary.

        Arguments:
            name (str): The name of the property to get.

        Returns:
            -: The value of the property.
        """
        item = self.get(name)
        return item.value if item else item

    def __setitem__(self, name, value):
        """Set the value of a child property.

        Arguments:
            name (str): The name of the property to set.
            value (-): The value to set.
        """
        _property = self.get(name)
        if _property:
            _property.value = value
        else:
            super(PropertiesDictionaryValue, self).__setitem__(name, value)
