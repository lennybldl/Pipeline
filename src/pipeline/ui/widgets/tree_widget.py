"""Manage the application tree widgets."""

from python_core.types import strings
from python_core.pyside2.widgets import tree_widget

from pipeline.internal import manager
from pipeline.ui.internal import synchronizer
from pipeline.ui.widgets import tree_widget_item

DATABASE = manager.Database()


class AbstractTreeWidget(tree_widget.TreeWidget):
    """Manage the abstraction for the tree widgets."""

    synchronizer = synchronizer.Synchronizer()

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(AbstractTreeWidget, self).__init__(*args, **kwargs)

        # register the tree widget to the synchronizer
        setattr(self.synchronizer, strings.lower_case(self.__class__.__name__), self)

        # initialize the tree widget
        self.setHeaderHidden(True)

    def sync(self, *args, **kwargs):
        """Synchonize the tree widget with the project project."""


class AbstractStepsTreeWidget(AbstractTreeWidget):
    """Manage the abstract steps tree widget."""

    item_class = tree_widget_item.AbstractMemberTreeWidgetItem

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(AbstractStepsTreeWidget, self).__init__(*args, **kwargs)

        # initialize the tree widget
        self.set_drag_drop(True)

        # signals
        self.currentItemChanged.connect(
            lambda item: self.synchronizer.sync_design_trees_selection(item._id)
        )

    def sync(self, *args, **kwargs):
        """Synchonize the tree widget with the pipeline project."""

        super(AbstractStepsTreeWidget, self).sync(*args, **kwargs)

        self.clear()

        # populate with the project
        project = DATABASE.project
        if not project:
            return

        # add the abstract items
        created_items = dict()
        for _id in project.get("abstract.id").keys():
            _id = project.get_abstract_step_id(_id)

            # create the actual item
            item = self.add_item(_id.name, parent=created_items.get(_id.parent, None))
            item._id = _id

            # add the created item to the dictionary of created items
            created_items[_id] = item

        self.expandAll()


class ConcreteStepsTreeWidget(AbstractTreeWidget):
    """Manage the abstract steps tree widget."""

    item_class = tree_widget_item.AbstractMemberTreeWidgetItem

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(ConcreteStepsTreeWidget, self).__init__(*args, **kwargs)

        # signals
        self.currentItemChanged.connect(
            lambda item: self.synchronizer.sync_concrete_tree_selection(item._id)
        )

    def sync(self, *args, **kwargs):
        """Synchonize the tree widget with the pipeline project."""

        super(ConcreteStepsTreeWidget, self).sync(*args, **kwargs)

        self.clear()

        # populate with the project
        project = DATABASE.project
        if not project:
            return

        # add the concrete items
        created_items = dict()
        for _id in project.get("concrete.id").keys():
            _id = project.get_concrete_step_id(_id)

            # create the actual item
            item = self.add_item(
                _id.get_name(),
                parent=created_items.get(_id.parent, None),
                tooltip=_id.get_path(),
            )
            item._id = _id

            # add the created item to the dictionary of created items
            created_items[_id] = item

        self.expandAll()
