"""Manage a menu bar to add menus to the app."""

import os

from PySide2.QtWidgets import QComboBox, QListWidget, QStyleFactory
from PySide2.QtGui import QIcon
from python_core.pyside2.widgets import menu_bar

from pipeline.api.checks import git
from pipeline.api.maya_api import maya_asset, exports, creation, studient_warning
from pipeline.api.maya_api.tools import rig
from pipeline.ui.dialogs import dialogs, popups
from pipeline.ui.tools import references_manager, export_animations
from pipeline.ui.images import images
from pipeline.utils import database


class AppMenuBar(menu_bar.MenuBar):

    _name = "AppMenuBar"
    maya_icon = images.get("maya.png")

    def __init__(self, *args, **kwargs):
        """Initialize the app menu bar."""

        super(AppMenuBar, self).__init__(*args, **kwargs)

        # initialize usefull classes
        self.db = database.Database()
        self.asset = maya_asset.MayaAsset()

    # edit UI

    def populate(self):
        """Poulate the app menu bar with menus."""

        # add the files menu
        self._files_menu()

        # add the tools menu
        self._tools_menu()

    def _files_menu(self):
        """Create and manage the files menu."""

        # add file management menus
        files_menu = self.add_menu("Files")
        files_menu.add_action(
            "New",
            triggered=self.create_new,
            tooltip=self.create_new.__doc__,
            shortcut="CTRL+N",
        )
        files_menu.add_action(
            "Increment Save",
            triggered=self.increment_save,
            tooltip="(MAYA) " + self.increment_save.__doc__,
            icon=self.maya_icon,
            shortcut="CTRL+Shift+S",
        )
        files_menu.add_action(
            "Import",
            triggered=self.import_model,
            tooltip="(MAYA) " + "import something in the current scene.",
            icon=self.maya_icon,
            shortcut="CTRL+I",
        )
        # add a recent menu to open recent files
        self.recent_menu = files_menu.add_menu("Recent")
        self.populate_recents()

        # add actions on the selected item
        files_menu.add_separator()
        selected_asset_menu = files_menu.add_menu("Selected Asset")
        selected_asset_menu.add_action(
            "Open Asset Path",
            triggered=lambda: self.open_path(open_task=False),
            tooltip="Open the path to the selected asset.",
        )
        selected_asset_menu.add_action(
            "Open Asset Task Path",
            triggered=self.open_path,
            tooltip="Open the path to the selected asset task.",
        )
        selected_asset_menu.add_action(
            "Create task",
            triggered=self.create_task,
            tooltip="Create the current selected task for the current selected item.",
        )
        selected_asset_menu.add_action(
            "Deduce WIP from DEF",
            triggered=self.deduce_wip_from_def,
            tooltip=self.deduce_wip_from_def.__doc__,
        )

        # add export / publish methods
        files_menu.add_separator()
        files_menu.add_action(
            "Save DEF",
            triggered=self.save_def,
            tooltip="(MAYA) " + self.save_def.__doc__,
            icon=self.maya_icon,
        )
        files_menu.add_action(
            "Export",
            triggered=self.export,
            tooltip="(MAYA) " + self.export.__doc__,
            icon=self.maya_icon,
        )
        files_menu.add_action(
            "Publish Unreal",
            triggered=self.publish,
            tooltip="(MAYA) " + self.publish.__doc__,
            icon=self.maya_icon,
        )

        files_menu.add_separator()
        files_menu.add_action(
            "Git sanity check",
            triggered=self.git_sanity_checks,
            tooltip=self.git_sanity_checks.__doc__,
        )
        files_menu.add_action(
            "Studient warnings",
            triggered=self.studient_warnings,
            tooltip=self.studient_warnings.__doc__,
        )

        files_menu.add_separator()
        files_menu.add_action(
            "Save DEF / Publish / Git",
            triggered=self.finish_asset,
            tooltip="(MAYA) " + self.finish_asset.__doc__,
            icon=self.maya_icon,
        )

        # set the style for every menus
        for menu in [files_menu, self.recent_menu, selected_asset_menu]:
            menu.setStyle(QStyleFactory.create("Fusion"))

    def _tools_menu(self):
        """Create and manage the tools menu."""

        # add a tools menu
        tools_menu = self.add_menu("Tools")

        # add a texture menu to manipulate textures
        texturing_menu = tools_menu.add_menu("Texturing", tearoff=True)
        texturing_menu.add_action(
            "Open Path",
            triggered=self.open_texture_path,
            tooltip=self.open_texture_path.__doc__,
        )
        texturing_menu.add_action(
            "Create task",
            triggered=lambda: self.create_task("texturing"),
            tooltip="Create the texturing task on the current selected item.",
        )

        # add a rig menu
        rig_menu = tools_menu.add_menu("Rig", tearoff=True)
        rig_menu.add_action(
            "Update/Import model",
            triggered=self.update_model,
            tooltip="(MAYA) " + self.update_model.__doc__,
            icon=self.maya_icon,
        )
        rig_menu.add_separator()
        rig_menu.add_action(
            "Set joints to export",
            triggered=rig.set_joints_to_export,
            tooltip="(MAYA) " + rig.set_joints_to_export.__doc__,
            icon=self.maya_icon,
        )
        rig_menu.add_action(
            "Select joints to export",
            triggered=rig.select_joints_to_export,
            tooltip="(MAYA) Select the selected joints saved in the pipe node.",
            icon=self.maya_icon,
        )

        # add a layout / animation menu
        layout_menu = tools_menu.add_menu("Layout / animation", tearoff=True)
        layout_menu.add_action(
            "References manager",
            triggered=self.references_manager,
            tooltip="(MAYA) " + self.references_manager.__doc__,
            icon=self.maya_icon,
        )
        layout_menu.add_action(
            "Export animations",
            triggered=self.export_animations,
            tooltip="(MAYA) " + self.export_animations.__doc__,
            icon=self.maya_icon,
        )

        # set the styje for every menus
        for menu in [tools_menu, texturing_menu, rig_menu, layout_menu]:
            menu.setStyle(QStyleFactory.create("Fusion"))

    def populate_recents(self):
        """Populate the recent menu with the last opened files."""

        prefs = self.db.prefs

        recents = prefs.get("recents", None)

        self.recent_menu.clear()
        if recents is not None:
            temp = recents
            for file in temp:
                # check if the file still exists. If not delete it from the prefs
                if not os.path.exists(
                    os.path.join(self.asset.get_path_from_name(file), file)
                ):
                    recents.remove(file)
                    continue

                self.recent_menu.add_action(
                    file,
                    triggered=lambda skip=None, _file=file: self.open_recent(_file),
                    tooltip="(MAYA) Open the file in maya.",
                )

            prefs.update({"recents": recents})
            self.db.prefs = prefs

    def get_assets_informations_from_ui(self):
        """Get the asset naming informations from the ui.

        :return: The asset type, asset name and asset task
        :rtype: tuple
        """

        # get ui elements
        main_window = self.topLevelWidget()

        asset_type_ui = main_window.findChild(QComboBox, "AssetTypeComboBox")
        task_type_ui = main_window.findChild(QComboBox, "TaskTypeComboBox")
        list_widget_ui = main_window.findChild(QListWidget, "AssetsListWidget")

        # get information from ui
        asset_type = asset_type_ui.currentText()
        task = task_type_ui.currentText()

        # get the selected assets
        assets = list_widget_ui.selectedItems()
        if not assets:
            raise ValueError("# Pipeline : No asset is currently selected")

        return asset_type, assets[0].text(), task

    # create assets

    def create_new(self):
        """Create a new asset."""

        dialog = dialogs.CreateNewDialog(parent=self.topLevelWidget())
        dialog.exec_()

    def create_task(self, task=None):
        """Create a task at the right location for the current selected item.

        :param task: The task to create if specifyied.
            Else it will create the current asste task.
        :type task: str
        """

        # get ui elements
        asset_type, assets_name, current_task = self.get_assets_informations_from_ui()

        # force the task or not
        if task is None:
            task = current_task

        # deduce the asset task name to create it
        asset_task_name = self.asset.get_asset_task_name(assets_name, task)

        # build a dialog to ask if we want to create a new task
        dialog = dialogs.YesNoDialog()
        # set the elements to display in the dialog
        dialog.title = "Create {}?".format(task)
        dialog.title_msg = task.upper()
        dialog.msg = "No {} task found.\nStart one?".format(task)
        if not dialog.exec_():
            print("# Pipeline : No {} task was created".format(task))
            return

        # create the task
        if self.asset.create(asset_task_name) is None:
            print("# Pipeline : " + asset_task_name + " already exists")

    def import_model(self):
        """Import a model."""

        from maya import cmds

        cmds.Import()

    # interact with assets

    def deduce_wip_from_def(self):
        """Copy the DEF version of the asset to the WIP folder"""

        # get informations from ui
        asset_type, assets_name, task = self.get_assets_informations_from_ui()

        self.asset.deduce_wip_from_def(
            self.asset.get_asset_task_name(assets_name, task)
        )

    def increment_save(self):
        """Save the current scene as an increment."""

        dialog = dialogs.IncrementSaveDialog(parent=self.topLevelWidget())
        comment = dialog.exec_()

        if comment is not False:
            creation.increment_save(comment)

        # update the ui with the recently opened files
        self.populate_recents()

    def open_recent(self, name):
        """Open the recent file we clicked on in maya.

        :param name: The file name to open
        :type name: str
        """

        from maya import cmds

        path = os.path.join(self.asset.get_path_from_name(name), name)

        # if can't find the file : remove it from prefs and raise an error
        if not os.path.exists(path):
            # update the ui
            self.populate()

            raise ValueError(
                "# Pipeline : Can't find {}. The file may not exist anymore.".format(
                    path
                )
            )

        cmds.file(path, open=True, force=True)

        # save the opend file as a recently opend file
        self.asset.update_recents(os.path.basename(path))
        self.populate_recents()

    def open_path(self, open_task=True):
        """Open the path to the selected item.

        :param open_task: Wether or not to open the path of the task or of the asset.
        :type open_task: bool
        """

        # get ui elements
        asset_type, assets_name, task = self.get_assets_informations_from_ui()

        # open the path to the file
        if open_task:
            self.asset.open_path(self.asset.get_asset_task_name(assets_name, task))
        else:
            self.asset.open_path(assets_name)

    def open_texture_path(self):
        """Open the texture path to the selected item."""

        # get ui elements
        asset_type, assets_name, task = self.get_assets_informations_from_ui()

        # open the path to the file
        self.asset.open_path(self.asset.get_asset_task_name(assets_name, "texturing"))

    # tools

    def update_model(self):
        """Update the model in the rig scene."""

        # build a dialog to ask if we want to create a new task
        dialog = dialogs.YesNoDialog()
        # set the elements to display in the dialog
        dialog.title = "Update/Import Model?"
        dialog.title_msg = "This will delete the current GEO group!"
        dialog.title_msg_color = "red"
        msg = [
            "Are you sure you want to update the model?",
            "You should increment first!",
            "This will delete the current GEO group!",
        ]
        dialog.msg = "\n".join(msg)
        if not dialog.exec_():
            print("# Pipeline : Update model aborted")
            return

        # update the model
        rig.update_model()

    def references_manager(self):
        """Open the references manager in the current scene."""

        # get ui elements
        main_window = self.topLevelWidget()

        manager = references_manager.ReferencesManager(parent=main_window)
        manager.populate()
        manager.show()

    def export_animations(self):
        """Export the animations for unreal."""

        # get informations on the current file
        informations = self.asset.get_informations_from_current_file()
        asset_type, basename, task, version, comment, path = informations

        if task != "animation":
            raise RuntimeError(
                "# Pipeline : The assets only can be exported from an animation scene."
            )

        # get ui elements
        main_window = self.topLevelWidget()

        exporter = export_animations.ExportAnimations(main_window)
        exporter.populate()
        exporter.show()

    # exports / publish

    def save_def(self):
        """Save the current asset in the DEF folder to publish it on git."""

        if popups.confirm("Save def?"):
            # ask if we want to save the file before
            popups.save_popup()

            # export the asset
            exports.save_def()

    def export(self):
        """Export the current asset to import it in an other soft or an other way."""  # noqa E501

        if popups.confirm("Export current scene?"):
            # ask if we want to save the file before
            popups.save_popup()

            # export the asset
            exports.export()

    def publish(self):
        """Publish the current asset to import it in unreal."""

        if popups.confirm("Publish current scene?"):
            # ask if we want to save the file before
            popups.save_popup()

            # export the asset
            exports.publish()

    def git_sanity_checks(self):
        """Make sure now WIP folder will be gited nor oversized files."""

        git.update_gitignore()
        git.ignore_oversized_files()

    def studient_warnings(self):
        """Remove the studient warning from the files in 'export' or 'DEF'"""

        # build a dialog to ask if we want to create a new task
        dialog = dialogs.YesNoDialog()
        # set the elements to display in the dialog
        dialog.setWindowIcon(QIcon(images.get("lapin")))
        dialog.title = "Get rid of studient warning?"
        dialog.title_msg = "This will modify every 'DEF' and 'Export' maya file"
        dialog.title_msg_color = "red"
        msg = [
            "Si tu ne t'appelle ni Lenny ni Lucile, ne clique pas sur ce bouton.",
            "Tu risques de te faire tres tres mal!",
        ]
        dialog.msg = "\n".join(msg)
        if not dialog.exec_():
            print("# Pipeline : Studient warning aborted")
            return

        studient_warning.remove_from_all_files(["DEF", "export"])

    def finish_asset(self):
        """Finish the asset to publish it in the pipe and save it on git.

        - Save a DEF version of the asset
        - publish it to unreal
        - launch the git sanity checks.
        """

        if popups.confirm("Save DEF and publish this asset?"):
            # ask if we want to save the file before
            popups.save_popup()

        # do the exports
        exports.save_def()
        exports.publish()
        self.git_sanity_checks()
