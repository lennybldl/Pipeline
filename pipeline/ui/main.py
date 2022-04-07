"""Manage the pipeline main window."""

from python_core.pyside2 import base_ui

from pipeline.ui.body import app_menu_bar, open_create, workspace_path
from pipeline.ui.images import images
from pipeline.utils import database


class Main(base_ui.MainWindow):
    """Manage the main window."""

    _title = "Pipeline 1.0.0"
    _name = "MainWindow"
    _icon = images.get("pipe")

    def __init__(self, *args, **kwargs):
        """initialise the main window."""

        super(Main, self).__init__(*args, **kwargs)

        # make sure the app runs on safe basis
        db = database.Database()
        db.start_checks()

    def populate(self):
        """Populate themain window UI."""

        main_layout = self.main_widget.layout
        main_layout.set_alignment("top")

        # create a menu bar
        menu = app_menu_bar.AppMenuBar()
        menu.populate()
        main_layout.addWidget(menu)

        # populate the app ui in an other layout that has padding
        layout = main_layout.add_layout("vertical")

        # add the workspace path
        path = workspace_path.WorkspacePath()
        path.populate()
        layout.addWidget(path)

        # add the open create
        self.open_create_lay = open_create.OpenCreate()
        self.open_create_lay.populate()
        layout.addLayout(self.open_create_lay)
        self.open_create_lay.populate_asset_list()
