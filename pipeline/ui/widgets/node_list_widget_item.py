"""Create a widget item linked to a maya node."""


from python_core.pyside2.widgets import list_widget_item


class NodeListWidgetItem(list_widget_item.ListWidgetItem):
    """Create an item linked to a maya node."""

    def __init__(self, *args, **kwargs):
        """Initialize the node list widget item."""

        super(NodeListWidgetItem, self).__init__(*args, **kwargs)

        self.node = None
