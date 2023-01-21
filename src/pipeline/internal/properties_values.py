"""Manage the properties values that make properties work.

Those are the objects stored in some properties to extend behaviours.
"""

from python_core.types import dictionaries


class DictionaryValue(dictionaries.Dictionary):
    """Manage the dictionaries in the properties."""

    parent = None

    def __getattribute__(self, name):
        """Get an attribute from the object or the dictionary content.

        Arguments:
            name (str): The name of the attribute or property.

        Returns:
            -: The attribute.
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            attribute = self.get(name, AttributeError)
            if attribute is AttributeError:
                raise AttributeError(
                    "'{}' has no attribute '{}'".format(self.parent.__class__, name)
                )
            return attribute
