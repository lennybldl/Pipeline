"""Add a layout that to open an create assets tasks."""

from PySide2.QtWidgets import QMenuBar
from python_core.pyside2.widgets import layout

from pipeline.api.assets import assets
from pipeline.ui.widgets import assets_list_widget, list_filter_bar
from pipeline.utils import database


class OpenCreate(layout.VBoxLayout):
    """Manage files to open or create."""

    def __init__(self, *args, **kwargs):
        """Initialize the layout."""

        super(OpenCreate, self).__init__(*args, **kwargs)

        # initialize useful classes
        self.db = database.Database()
        self.assets = assets.Assets()

    # edit UI

    def populate(self):
        """Populate the ui with buttons to interact."""

        # get the app data
        data = self.db.app_data

        # build tasks
        layout = self.add_layout("horizontal")
        self.asset_type = layout.add_combo_box(
            data["assets"].keys(),
            tooltip="The type of asset to open/create.",
        )
        self.asset_type.setObjectName("AssetTypeComboBox")
        self.task_type = layout.add_combo_box(
            tooltip="The kind of task to open/create for the current selected item."
        )
        self.task_type.setObjectName("TaskTypeComboBox")

        # create a filtyer bar to filter a task list
        layout = self.add_layout("horizontal")
        self.filter_bar = list_filter_bar.FilterBar()
        layout.addWidget(self.filter_bar)
        self.task_type_filter = layout.add_combo_box(tooltip="Filter by task type.")
        self.task_type_filter.setObjectName("TaskTypeFilterComboBox")

        # build the tasks list representation
        self.list_widget = assets_list_widget.AssetsListWidget(
            tooltip=assets_list_widget.AssetsListWidget.__doc__
        )
        self.addWidget(self.list_widget)

        # set the list widget to be filtered by the filter bar
        self.filter_bar.list_widget = self.list_widget

        # build the open
        lay = self.add_layout("horizontal")
        lay.add_button(
            "Open latest",
            clicked=self.open_latest,
            tooltip="(MAYA) " + self.open_latest.__doc__,
        )
        lay.add_button(
            "Open specific",
            clicked=self.open_specific,
            tooltip="(MAYA) " + self.open_specific.__doc__,
        )

        # initialise the ui
        self.set_prefs()
        self.sync_tasks()
        self.set_prefs()

        # connect signals
        self.asset_type.currentTextChanged.connect(self.save_prefs)
        self.asset_type.currentTextChanged.connect(self.sync_tasks)
        self.asset_type.currentTextChanged.connect(self.populate_asset_list)

        self.task_type.currentTextChanged.connect(self.save_prefs)

        self.task_type_filter.currentTextChanged.connect(self.save_prefs)
        self.task_type_filter.currentTextChanged.connect(self.populate_asset_list)

    def update_recents_menu(self):
        """Update the recents menu with the recently opened files."""

        main_window = self.parent().parent().parent().topLevelWidget()

        menu_bar = main_window.findChild(QMenuBar, "AppMenuBar")
        menu_bar.populate_recents()

    def populate_asset_list(self):
        """Populate the asset list widget depending on the ui."""

        self.list_widget.populate(
            self.asset_type.currentText(),
            self.task_type_filter.currentText(),
        )

    def sync_tasks(self):
        """Synchronise the tasks and tasks filter with assets type.

        It is used to display only the tasks that can be created on this asset type.
        """

        data = self.db.app_data

        # get the current asset type
        asset_type = self.asset_type.currentText()
        # get the tasks to display
        tasks = data["assets"][asset_type]["tasks"]

        # get current task type text
        task_type = self.task_type.currentText()
        if task_type not in tasks:
            # set the tasks text
            self.task_type.clear()
            self.task_type.add_items(tasks)

        # get current filter task text
        filter_task = self.task_type_filter.currentText()

        # set the tasks text
        self.task_type_filter.clear()
        self.task_type_filter.add_items(["all"] + tasks)

        if filter_task in tasks:
            self.task_type_filter.setCurrentText(filter_task)

    def get_selected_asset_task(self):
        """Get the select asset task type from the ui.

        :return: The asset task name
        :rtype: str
        """

        # get the selected items in the list widget
        assets = self.list_widget.selectedItems()
        if not assets:
            raise ValueError(
                "# Pipeline : No asset is currently selected in list widget."
            )

        # get the current task to open
        task = self.task_type.currentText()

        # return the asset task name
        return self.assets.get_asset_task_name(assets[0].text(), task)

    # perform

    def open_latest(self):
        """Open the latest version of the selected item."""

        # open the latest file
        self.assets.open_latest(self.get_selected_asset_task())
        self.update_recents_menu()

    def open_specific(self):
        """Open a specific version of the selected item."""

        # open the latest file
        self.assets.open_specific(self.get_selected_asset_task())
        self.update_recents_menu()

    # manage data

    def save_prefs(self):
        """Save current ui prefs."""

        prefs = self.db.prefs

        prefs.update(
            {
                "current_assets": self.asset_type.currentText(),
                "current_tasks": self.task_type.currentText(),
                "current_tasks_filter": self.task_type_filter.currentText(),
            }
        )

        self.db.prefs = prefs

    def set_prefs(self):
        """Edit the ui with the saved prefs."""

        prefs = self.db.prefs

        if prefs.get("current_assets", False):
            self.asset_type.setCurrentText(prefs["current_assets"])

        if prefs.get("current_tasks", False):
            self.task_type.setCurrentText(prefs["current_tasks"])

        if prefs.get("current_tasks_filter", False):
            self.task_type_filter.setCurrentText(prefs["current_tasks_filter"])
