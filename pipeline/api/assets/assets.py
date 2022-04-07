"""Manage the project assets."""

import os
import shutil

from python_core.pyside2 import base_ui

from pipeline.api.assets import paths


class Assets(paths.Paths):
    """Manage the assets."""

    # scenes creation

    def create(self, name):
        """Create an asset in the right path depending on the asset name.

        If name is the asset name : only create the asset folder
        If name is the asset task name : create the asset task folder
        If name is a file name : create the file in the right directory

        :param name: The asset name
        :type name: str

        :return: The full path to the created asset, None if nothing was created.
        :rtype: str, None
        """

        app_data = self.db.app_data

        # get information from the name
        splitted_name = name.split("_")

        # create the asset folder
        if len(splitted_name) == 2:
            path = self.get_path_from_name(name)
            if self.create_directories(path):
                print("# Pipeline : Created -> " + path)
                return path

        # create the asset task folder
        elif len(splitted_name) > 2:
            # create every tasks subfiles from
            path = self.get_path_from_name(name).replace(r"\WIP", "")
            task = self.get_informations_from_name(name)[2]
            results = list()
            for folder in app_data["tasks"][task]["folders"]:
                results.append(self.create_directories(os.path.join(path, folder)))

            # create the file too
            if len(splitted_name) > 3:
                # create the maya file
                from pipeline.api.maya_api import creation

                path = creation.create_maya_scenes(name)
                print("# Pipeline : Created -> " + path)
                return path

            else:
                if max(results):
                    print("# Pipeline : Created -> " + path)
                    return path

        return None

    def open_latest(self, name):
        """Open the latest scene for this asset task name.

        :param name: The asset task name to open.
        :type name: str
        """

        from maya import cmds
        from pipeline.ui.dialogs import popups, dialogs

        # get informations from the name
        informations = self.get_informations_from_name(name)
        asset_type, basename, task, version, comment, path = informations

        # get the directory the file is stored in
        directory = self.get_path_from_name(name)
        latest_file = self.get_latest_file(directory, ".ma")

        # if the latest file doesn't exists, try to deduce it from def
        if not latest_file:
            self.deduce_wip_from_def(name)
        latest_file = self.get_latest_file(directory, ".ma")

        # if there is no file, ask if we want to create one
        if latest_file is None:
            # build a dialog to ask if we want to create a new scene
            dialog = dialogs.YesNoDialog()

            # set the elements to display in the dialog
            dialog.title = "Create {}?".format(task)
            dialog.title_msg = task.upper()
            dialog.msg = "No {} task found.\nStart one?".format(task)

            if not dialog.exec_():
                print("# Pipeline : No {} task was created".format(task))
                return

            # create the new scene
            path = self.create(name + "_000.ma")

        else:
            # get the full path to the latest file
            path = os.path.join(directory, latest_file)

        # save the current file before
        popups.save_popup()

        # open the file in maya
        cmds.file(path, open=True, force=True)

        # save the opend file as a recently opend file
        self.update_recents(os.path.basename(path))

        print("# Pipeline : Open latest -> " + path)

    def open_specific(self, name):
        """Open a specific version of an asset.

        :param name: The asset task name to open.
        :type name: str
        """

        from maya import cmds
        from pipeline.ui.dialogs import popups

        # get informations from the name
        informations = self.get_informations_from_name(name)
        asset_type, basename, task, version, comment, path = informations

        # get the directory the file is stored in
        directory = self.get_path_from_name(name)

        if not self.get_latest_file(directory, ".ma"):
            print(
                '# Pipeline : The asset "{}" task is empty.'.format(task)
                + " Maybe try deducing WIP from DEF."
            )
            return

        # browse to the directory to get the file to open
        dialog = base_ui.BrowseDialog()
        dialog.title = "Browse to file"

        file = dialog.browse(directory=directory, extensions=".ma")
        if file is None:
            return

        # save before
        popups.save_popup()

        # open the selected file
        cmds.file(file[0], open=True, force=True)

        # save the opend file as a recently opend file
        self.update_recents(os.path.basename(file[0]))

        print("# Pipeline : Open specific -> " + file[0])

    def deduce_wip_from_def(self, name):
        """Copy the DEF version of the asset to the WIP folder.

        :param name: The asset task name to open.
        :type name: str
        """

        from pipeline.ui.dialogs import popups

        # get the directories to copy and paste from
        source_directory = self.get_path_from_name(name, def_path=True)
        destination_directory = self.get_path_from_name(name)

        # get the latest DEF file
        file_name = self.get_latest_file(source_directory, ".ma")
        if not file_name:
            print("# Pipeline : No DEF file found.")
            return

        # deduce the source and destination files
        source = os.path.join(source_directory, file_name)
        destination = os.path.join(destination_directory, file_name)

        # make sure the directories exist
        self.create_directories(source_directory)
        self.create_directories(destination_directory)

        # copy the DEF file
        if os.path.exists(destination):
            if not popups.confirm(
                "A WIP file already exists with the name "
                + file_name
                + "\nDo you want to replace it?"
            ):
                print("# Pipeline : Deduce WIP from DEF aborted.")
                return

        shutil.copy2(source, destination)
        print('# Pipeline : DEF file "{}" set as WIP.'.format(file_name))

    # data management

    def update_recents(self, file):
        """Update list of recently opened maya files.

        :param file: The complete path to the file.
        :type file: str
        """

        prefs = self.db.prefs

        recents = prefs.get("recents", None)

        if recents is None:
            prefs.update({"recents": [file]})

        else:
            # save the 10 last opened files
            if file in recents:
                recents.remove(file)

            recents.insert(0, file)
            if len(recents) > 10:
                recents.pop(-1)
            prefs.update({"recents": recents})

        # save the prefs
        self.db.prefs = prefs
