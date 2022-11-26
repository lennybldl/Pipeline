"""Manage the list widget items."""


from python_core.pyside2.widgets import list_widget_item


class AbstractMemberListWidgetItem(list_widget_item.ListWidgetItem):
    """Manage the methods for an member list widget item."""

    _id = None  # Member: The id of the member


class ConceptListWidgetItem(AbstractMemberListWidgetItem):
    """Manage the methods for a concept list widget item."""


class StaticConceptListWidgetItem(ConceptListWidgetItem):
    """Manage the methods for a static list widget item.

    An item that can not completely be edited.
    """

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(StaticConceptListWidgetItem, self).__init__(*args, **kwargs)
        self.set_color("#636b78")
