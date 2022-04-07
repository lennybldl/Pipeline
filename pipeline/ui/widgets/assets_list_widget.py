"""Manage the created assets widgets."""

import os

from PySide2.QtCore import Qt
from python_core.pyside2.widgets import list_widget

from pipeline.utils import database


class AssetsListWidget(list_widget.ListWidget):
    """Display every assets in the project by task."""

    _name = "AssetsListWidget"

    def __init__(self, *args, **kwargs):
        """Initialize the line edit."""

        super(AssetsListWidget, self).__init__(*args, **kwargs)

        self.setFocusPolicy(Qt.NoFocus)

        # use the database to get data
        self.db = database.Database()

    def populate(self, asset_type, task_type):
        """Populate the list widget with tasks to do.

        :param asset_type: The asset type (props, character, shots...)
        :type asset_type: str
        :param task_type: The task type (all, modeling, rig, texturing...)
        :type task_type: str
        """

        self.clear()

        # get app_data
        app_data = self.db.app_data
        prefs = self.db.prefs

        # get the workspace we're working in
        workspace = prefs.get("workspace", None)
        if workspace is None:
            return

        # list all the assets in the asset type directory
        assets_path = os.path.join(workspace, app_data["assets"][asset_type]["path"])
        if not os.path.exists(assets_path):
            return

        # display all the files corresponding to the asset type and the current task
        prefix = app_data["assets"][asset_type]["prefix"]
        for asset in os.listdir(assets_path):
            if asset.startswith(prefix):
                if task_type == "all":
                    self.add_item(asset)
                else:
                    task_path = os.path.join(assets_path, asset, task_type)
                    if os.path.exists(task_path) and os.listdir(task_path):
                        self.add_item(asset)
