"""Manage the application list widgets."""

from python_core.types import strings
from python_core.pyside2.widgets import list_widget

from pipeline.internal import database
from pipeline.ui.internal import synchronizer
from pipeline.ui.widgets import list_widget_item

DATABASE = database.Database()


class AbstractListWidget(list_widget.ListWidget):
    """Manage the abstraction for the list widgets."""

    synchronizer = synchronizer.Synchronizer()

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(AbstractListWidget, self).__init__(*args, **kwargs)

        # register the list widget to the synchronizer
        setattr(self.synchronizer, strings.lower_case(self.__class__.__name__), self)

    def sync(self, *args, **kwargs):
        """Synchonize the list widget with the project config."""


class ConceptsListWidget(AbstractListWidget):
    """Manage the concepts list widget."""

    def __init__(self, *args, **kwargs):
        """Initialize the widget."""

        super(ConceptsListWidget, self).__init__(*args, **kwargs)

        self.currentItemChanged.connect(
            lambda item: self.synchronizer.sync_design_trees_selection(item._id)
        )

    # methods

    def sync(self, *args, **kwargs):
        """Synchonize the list widget with the project config."""

        super(ConceptsListWidget, self).sync()

        self.clear()

        # populate with the config
        config = DATABASE.config
        if not config:
            return

        # add the concept items
        static_ids = database.STATIC_CONCEPTS.values()
        for _id in config.get("concepts.id").keys():
            _id = config.get_concept_id(_id)

            # set the type of list widget item to create
            if _id in static_ids:
                item_class = list_widget_item.StaticConceptListWidgetItem
            else:
                item_class = list_widget_item.ConceptListWidgetItem

            # create the actual item
            item = self.add_item(_id.name, item_class=item_class)
            item._id = _id
