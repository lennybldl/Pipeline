"""Create the ui to define the workspace body."""

from PySide2.QtWidgets import QComboBox, QListWidget

from python_core.pyside2 import base_ui

from pipeline.utils import database


class WorkspacePath(base_ui.Widget):
    """Create a layout to manage the workspace path."""

    def __init__(self, *args, **kwargs):
        """Initialize the layout."""

        super(WorkspacePath, self).__init__(*args, **kwargs)

        self.db = database.Database()

    def populate(self):
        """Populate the workspace path with buttons to interact."""

        self.layout.setContentsMargins(0, 0, 0, 0)

        self.layout.add_label("Workspace Path : ")

        lay = self.layout.add_layout("horizontal")
        self.path = lay.add_line_edit(
            placeholder=r"C:\path\to\maya\project\...", tooltip="The maya project path."
        )
        self.path.editingFinished.connect(self.save_prefs)

        lay.add_button("Browse...", clicked=self.browse)

        self.set_prefs()

    def browse(self):
        """Browse to the workspace path."""

        dialog = base_ui.BrowseDialog()
        dialog.title = "Browse to workspace"

        result = dialog.browse(file=False)

        # get the corresponding line edit
        if result is not None:
            self.path.set_text(result[0])
        else:
            self.path.set_text(reset=True)

        self.save_prefs()

        # update the asset list widget on the current project
        self.__update_asset_list()

    def save_prefs(self):
        """Save current ui prefs."""

        prefs = self.db.prefs

        prefs.update(
            {
                "workspace": self.path.text(),
            }
        )

        self.db.prefs = prefs

    def set_prefs(self):
        """Edit the ui with the saved prefs."""

        prefs = self.db.prefs

        if prefs.get("workspace", False):
            self.path.setText(prefs["workspace"])

    def __update_asset_list(self):
        """Update the asset list widget on the current project."""

        # update the list widget
        main_window = self.topLevelWidget()

        # find the ui elements
        asset_type_ui = main_window.findChild(QComboBox, "AssetTypeComboBox")
        task_type_ui = main_window.findChild(QComboBox, "TaskTypeComboBox")
        list_widget_ui = main_window.findChild(QListWidget, "AssetsListWidget")

        # update the asset list widget
        list_widget_ui.populate(asset_type_ui.currentText(), task_type_ui.currentText())
