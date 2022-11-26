"""Manage the synchronizer class.

This class is in charge of the communication between every member of the UI.
"""


class Synchronizer(object):
    """Manage the communications between the UI members."""

    _instance = None

    design_members_panel = None
    design_members_properties_panel = None

    def __new__(cls):
        """Override the __new__ method to always return the same instance."""
        if not cls._instance:
            cls._instance = super(Synchronizer, cls).__new__(cls)
        return cls._instance

    def sync_design_trees_selection(self, _id):
        """Synchronize the rest of the UI with the current design member selection."""

        if self.design_members_properties_panel:
            self.design_members_properties_panel.sync(_id)
