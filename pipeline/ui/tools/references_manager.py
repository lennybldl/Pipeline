"""Build the references manager editor."""

from python_core.pyside2 import base_ui

from pipeline.api.maya_api.tools import animation
from pipeline.ui import theme
from pipeline.ui.widgets import assets_list_widget, list_filter_bar
from pipeline.ui.dialogs import popups
from pipeline.utils import database


class ReferencesManager(base_ui.MainWindow):
    """Build a references manager UI."""

    _title = "Import references"

    def __init__(self, *args, **kwargs):
        """Initialize the references manager."""

        super(ReferencesManager, self).__init__(*args, **kwargs)

        self.resize(200, 350)

        self.db = database.Database()

    def populate(self, *args, **kwargs):
        """Populate the reference manager ui."""

        app_data = self.db.app_data

        # get the window layout
        layout = self.main_widget.layout

        # create a filter layout
        filter_layout = layout.add_layout("horizontal")

        # add filters
        self.filter_bar = list_filter_bar.FilterBar()
        filter_layout.addWidget(self.filter_bar)
        # add a combo box to select the asset to select
        self.asset_type = filter_layout.add_combo_box(
            app_data["assets"].keys(),
            tooltip="Filter the assets by type.",
        )

        # add a list widget to select the assets to import as reference
        self.list_widget = assets_list_widget.AssetsListWidget()
        layout.addWidget(self.list_widget)

        # set the list widget to be filtered by the filter bar
        self.filter_bar.list_widget = self.list_widget

        # create a filter layout
        import_layout = layout.add_layout("horizontal")

        # add button to import references
        import_layout.add_button(
            "Import reference",
            clicked=self.import_reference,
            tooltip=self.import_reference.__doc__,
        )
        self.import_count = import_layout.add_spin_box(
            value=1,
            min=1,
            tooltip="The number of times to import the selected asset as reference.",
        )
        self.import_count.setFixedWidth(60)

        # set the main window theme
        theme.theme(self)

        # edit the ui
        self.set_prefs()
        self.populate_asset_list()

        # connect signals
        self.asset_type.currentTextChanged.connect(self.save_prefs)
        self.asset_type.currentTextChanged.connect(self.populate_asset_list)

    def populate_asset_list(self):
        """Populate the asset list widget depending on the ui."""

        self.list_widget.populate(self.asset_type.currentText(), "all")

    def import_reference(self):
        """Import the current selected asset one or more times."""

        # get the number of time to import the references
        assets = self.list_widget.selectedItems()
        if not assets:
            raise ValueError("# Pipeline : No asset is currently selected")

        asset_name = assets[0].text()
        times = self.import_count.value()

        # display a popup to be fure to import those references
        if popups.confirm("Import - {} - {} time(s)".format(asset_name, times)):
            animation.import_reference(asset_name, times)

        times = self.import_count.setValue(0)

    # manage data

    def save_prefs(self):
        """Save current ui prefs."""

        prefs = self.db.prefs

        prefs.update(
            {
                "import_reference_assets_type": self.asset_type.currentText(),
            }
        )

        self.db.prefs = prefs

    def set_prefs(self):
        """Edit the ui with the saved prefs."""

        prefs = self.db.prefs

        if prefs.get("import_reference_assets_type", False):
            self.asset_type.setCurrentText(prefs["import_reference_assets_type"])
