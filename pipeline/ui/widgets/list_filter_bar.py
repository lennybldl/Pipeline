"""Create a filter bar to filter a list widget."""

from python_core.pyside2.widgets import line_edit


class FilterBar(line_edit.LineEdit):
    """Manage the filyter bar"""

    def __init__(self, *args, **kwargs):
        """Initialize the filter bar."""

        super(FilterBar, self).__init__(placeholder="filter", *args, **kwargs)

        # get the list widget to filter
        self.list_widget = None

        # filter the list widget every time the text changes
        self.textChanged.connect(self.update)

    def update(self):
        """Filter the list by items names."""

        # filter the list
        for item in self.list_widget.all_items():
            item.setHidden(False)
            if self.text() not in item.text():
                item.setHidden(True)
