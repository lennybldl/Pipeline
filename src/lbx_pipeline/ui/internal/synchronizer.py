"""Manage the synchronizer class.

This class is in charge of the communication between every member of the UI.
"""


class Synchronizer(object):
    """Manage the communications between the UI members."""

    _instance = None

    def __new__(cls):
        """Override the __new__ method to always return the same instance."""
        if not cls._instance:
            cls._instance = super(Synchronizer, cls).__new__(cls)
        return cls._instance
