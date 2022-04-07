"""Manage warnings ui."""

from python_core.pyside2 import base_ui
from python_core.types import strings

from pipeline.ui import theme
from pipeline.api.assets import assets
from pipeline.utils import database


class CreateNewDialog(base_ui.Dialog):
    """Manage a dialog to create a new asset."""

    _name = "CreateNewDialog"

    def __init__(self, *args, **kwargs):
        """Intisialize the widget."""

        super(CreateNewDialog, self).__init__(*args, **kwargs)
        self.title = "Create new asset"

        # initialize useful classes
        self.db = database.Database()
        self.assets = assets.Assets()

    def populate(self):
        """Populate the widget with elements."""

        # get the data dans the prefs
        data = self.db.app_data

        self.layout.setContentsMargins(8, 8, 8, 8)

        # built the ui to create a task
        layout = self.layout.add_layout("horizontal")
        self.asset_type = layout.add_combo_box(data["assets"].keys())
        self.asset_type.setObjectName("AssetTypeComboBox")

        self.asset_name = layout.add_line_edit("", placeholder="assetName")
        self.asset_name.editingFinished.connect(self.conform_name)

        self.create_button = layout.add_button("Create New", clicked=self.create_asset)
        self.create_button.setEnabled(False)

        # edit the ui with preferences
        self.set_prefs()

    def exec_(self):
        """Override the exec method to return a comment typed by the user."""

        # populate the dialog
        self.populate()

        # set the style for the window
        theme.theme(self)

        # execute the dialog
        super(CreateNewDialog, self).exec_()

    def conform_name(self):
        """Conform the asset name set in the line edit."""

        self.asset_name.blockSignals(True)

        # conform the asset name
        name = self.asset_name.text()
        if name:
            self.asset_name.setText(strings.camel_case(name, lower_first=True))
            self.create_button.setEnabled(True)
        else:
            self.create_button.setEnabled(False)

        self.asset_name.blockSignals(False)

    def create_asset(self):
        """Create the asset."""

        # just to be sure that the name will always be clear
        self.conform_name()

        # get name to create
        asset_type = self.asset_type.currentText()
        name = self.asset_name.text()
        # deduce the asset name
        asset_name = self.assets.get_asset_name(asset_type, name)

        # create the asset
        if self.assets.create(asset_name) is None:
            print("# Pipeline : " + asset_name + " already exists")

        # add the created file to the assets list widget
        main_window = self.parent()
        main_window.open_create_lay.populate_asset_list()

        # close the window
        self.create_button.setEnabled(False)
        self.asset_name.clear()

        self.accept()

    def set_prefs(self):
        """Edit the ui with the saved prefs."""

        prefs = self.db.prefs

        if prefs.get("current_assets", False):
            self.asset_type.setCurrentText(prefs["current_assets"])


class IncrementSaveDialog(base_ui.Dialog):
    """Manage a warning."""

    _name = "IncrementSaveDialog"

    def __init__(self, *args, **kwargs):
        """Intisialize the widget."""

        super(IncrementSaveDialog, self).__init__(*args, **kwargs)
        self.title = "Increment Save"

    def populate(self):
        """Populate the widget with elements."""

        self.layout.setContentsMargins(8, 8, 8, 8)

        # add a warning
        self.layout.add_label(
            "This will save your current scene\nand then increment it."
        )

        # add a field to ad a comment
        layout = self.layout.add_layout("horizontal")
        layout.add_label("Add comment :")
        self.comment = layout.add_line_edit("", placeholder="comment")
        self.comment.editingFinished.connect(self.conform_name)

        # add confirm buttons
        layout = self.layout.add_layout("horizontal")
        layout.add_button("Save", clicked=self.accept)
        layout.add_button("Cancel", clicked=self.reject)

    def exec_(self):
        """Override the exec method to return a comment typed by the user."""

        # populate the dialog
        self.populate()

        # set the style for the window
        theme.theme(self)

        # execute the dialog
        result = super(IncrementSaveDialog, self).exec_()

        # return the result of the dialog
        if result:
            if self.comment.text():
                return strings.camel_case(self.comment.text(), lower_first=True)
            return None

        return False

    def conform_name(self):
        """Conform the comment in the line edit."""

        self.comment.blockSignals(True)

        # conform the asset name
        comment = self.comment.text()
        if comment:
            self.comment.setText(strings.camel_case(comment, lower_first=True))

        self.comment.blockSignals(False)


class YesNoDialog(base_ui.Dialog):
    """Create a basic yes / no dialog"""

    _name = "YesNoDialog"

    def __init__(self, *args, **kwargs):
        """Intisialize the widget."""

        super(YesNoDialog, self).__init__(*args, **kwargs)
        self.title = "Dialog"
        self.title_msg = None
        self.title_msg_color = "#6FC7CA"
        self.msg = "Continue?"
        self.yes_label = "Yes"
        self.no_label = "No"

    def populate(self):
        """Populate the widget with elements."""

        self.layout.setContentsMargins(8, 8, 8, 8)

        # add a warning
        if self.title_msg:
            self.layout.add_label(self.title_msg, bold=True, color=self.title_msg_color)

        self.layout.add_label(self.msg)

        # add confirm buttons
        layout = self.layout.add_layout("horizontal")
        layout.add_button(self.yes_label, clicked=self.accept)
        layout.add_button(self.no_label, clicked=self.reject)

    def exec_(self):
        """Override the exec method to return a comment typed by the user."""

        # populate the dialog and set the style for the window
        self.populate()
        theme.theme(self)

        # execute the dialog
        return super(YesNoDialog, self).exec_()
