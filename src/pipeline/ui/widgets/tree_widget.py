"""Manage the application tree widgets."""

from python_core.types import strings
from python_core.pyside2.widgets import tree_widget

from pipeline.internal import database
from pipeline.ui.internal import synchronizer
from pipeline.ui.widgets import tree_widget_item

DATABASE = database.Database()


class AbstractTreeWidget(tree_widget.TreeWidget):
    """Manage the abstraction for the tree widgets."""

    synchronizer = synchronizer.Synchronizer()

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(AbstractTreeWidget, self).__init__(*args, **kwargs)

        # register the tree widget to the synchronizer
        setattr(self.synchronizer, strings.lower_case(self.__class__.__name__), self)

    def sync(self):
        """Synchonize the tree widget with the project config."""


class TheoreticalStepsTreeWidget(AbstractTreeWidget):
    """Manage the theoretical steps tree widget."""

    item_class = tree_widget_item.AbstractMemberTreeWidgetItem

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(TheoreticalStepsTreeWidget, self).__init__(*args, **kwargs)

        self.setHeaderHidden(True)
        self.set_drag_drop(True)

        self.currentItemChanged.connect(
            lambda item: self.synchronizer.sync_design_trees_selection(item._id)
        )

    def sync(self):
        """Synchonize the tree widget with the project config."""

        super(TheoreticalStepsTreeWidget, self).sync()

        self.clear()

        # populate with the config
        config = DATABASE.config
        if not config:
            return

        # add the theoretical items
        created_items = dict()
        for _id in config.get("theoreticals.id").keys():
            _id = config.get_theoretical_step_id(_id)

            # create the actual item
            item = self.add_item(_id.name, parent=created_items.get(_id.parent, None))
            item._id = config.get_theoretical_step_id(_id)

            # add the created item to the dictionary of created items
            created_items.update({_id: item})

        self.expandAll()
