"""Manage the tree widget items."""


from python_core.pyside2.widgets import tree_widget_item


class AbstractMemberTreeWidgetItem(tree_widget_item.TreeWidgetItem):
    """Manage the methods for an member tree widget item."""

    _id = None  # Member: The id of the member


class AbstractTreeWidgetItem(AbstractMemberTreeWidgetItem):
    """Manage the methods for a abstract tree widget item."""
