"""Manage the abstraction for the tabs."""

from python_core.pyside2 import base_ui
from python_core.types import strings

from pipeline.ui.internal import synchronizer


class AbstractTab(base_ui.Widget):
    """Manage the abstraction for the tab widgets."""

    synchronizer = synchronizer.Synchronizer()

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(AbstractTab, self).__init__(*args, **kwargs)

        # register the tree widget to the synchronizer
        setattr(self.synchronizer, strings.lower_case(self.__class__.__name__), self)

        self.build_ui()

    def build_ui(self):
        """Build the widget's UI"""

    def sync(self, *args, **kwargs):
        """Synchronize the widget with the rest of the UI"""
