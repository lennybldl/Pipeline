"""Build a UI to publish the animations in the current scene."""

from PySide2.QtCore import Qt

from python_core.pyside2 import base_ui

from pipeline.api.maya_api import exports
from pipeline.api.maya_api.tools import animation
from pipeline.ui import theme
from pipeline.ui.widgets import node_list_widget_item
from pipeline.ui.dialogs import popups


class ExportAnimations(base_ui.MainWindow):
    """Build an export animations manager UI."""

    _title = "Export animations"

    def __init__(self, *args, **kwargs):
        """Initialize the references manager."""

        super(ExportAnimations, self).__init__(*args, **kwargs)

        self.resize(180, 200)

    # edit the ui
    def populate(self):
        """Populate the UI with all the exportable animated assets."""

        layout = self.main_widget.layout

        # create a list widget to diplay the exportable assets in the scene
        self.list_widget = layout.add_list_widget()
        self.list_widget.setFocusPolicy(Qt.NoFocus)
        self.list_widget.setSelectionMode(self.list_widget.ExtendedSelection)
        self.list_widget.itemSelectionChanged.connect(self.maya_sync)
        self.populate_list_widget()

        # add buttons to export animations
        lay = layout.add_layout("horizontal")

        lay.add_button(
            "Export Selected",
            clicked=self.export_selected,
            tooltip="(MAYA) " + self.export_selected.__doc__,
        )
        lay.add_button(
            "Export All",
            clicked=self.export_all,
            tooltip="(MAYA) " + self.export_all.__doc__,
        )

        # set the main window theme
        theme.theme(self)

    def populate_list_widget(self):
        """Populate the list widget with all the exportable animated assets."""

        # list all the animated in the scene
        animateds = animation.get_exportable_animateds()

        for namespace in sorted(animateds.keys()):
            item = node_list_widget_item.NodeListWidgetItem(namespace)
            item.node = "{}:{}".format(namespace, animateds[namespace]["asset_name"])

            self.list_widget.addItem(item)

    def maya_sync(self):
        """Synchronize the list widget selection with the maya assets."""

        from maya import cmds

        # clear the current selection
        cmds.select(clear=True)

        # get the assets to export
        items = self.list_widget.selectedItems()
        if not items:
            return

        for item in items:
            cmds.select(item.node, add=True)

    # esport assets

    def export_all(self):
        """Bake and export all the assets in the scene."""

        # ask if we want to save first
        popups.save_popup()

        # export all the aniamtions
        exports.publish_animation()

    def export_selected(self):
        """Bake and export all selected assets."""

        # ask if we want to save first
        popups.save_popup()

        # get the assets to export
        items = self.list_widget.selectedItems()
        if not items:
            raise ValueError("# Pipeline : No asset selected")
        assets = [item.text() + ":RIG" for item in items]

        # export the animations on selected items
        exports.publish_animation(assets)
