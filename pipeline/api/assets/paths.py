"""Manipulate paths and names to get informations."""

import os
import subprocess

from python_core.types import strings

from pipeline.utils import database


class Paths(object):
    """Get informations on files from their name or path."""

    def __init__(self, *args, **kwargs):
        """Initialise the useful tools."""

        self.db = database.Database()

    # manage files and folders

    def create_directories(self, path):
        """Create a directories path if it doesn't already exists.

        :param path: The path to create
        :type path: str

        :return: True if path created, else false.
        :rtype: bool
        """

        # if the path to the scene doesn't exists create it
        if not os.path.exists(path):
            os.makedirs(path)
            return True

        return False

    # get informations

    def get_workspace(self, error=True):
        """Get the workspace path from prefs.

        :param error: Wether or not to throw error if the path is not specifyied.
        :type error: bool

        :return: The path to the workspace. None if not found.
        :rtype: str, None
        """

        prefs = self.db.prefs

        # get workspace
        workspace = prefs.get("workspace", False)
        if not workspace:
            if error:
                raise ValueError("# Pipeline : Please specify a workspace path first")
            else:
                return None

        return workspace.replace("/", "\\")

    def get_path_from_name(self, name, def_path=False):
        """Figure out the path to the name.

        If name is a task or file name : return task folder path.
        If name is on asset name : return asset folder path.

        :param name: The name to get the path from
        :type name: str
        :param def_path: Wether to return the DEF path or the WIP path
        :type def_path: bool

        :return: The path to name
        :rtype: str
        """
        # use app data to figure out paths
        app_data = self.db.app_data

        # get prefix from name
        splitted_name = name.split("_")

        # deduce asset type
        asset_type = self.get_asset_type_from_prefix(splitted_name[0])

        # if the name is the asset name
        if len(splitted_name) == 2:
            return os.path.join(
                self.get_workspace(),
                app_data["assets"][asset_type]["path"],
                name,
            ).replace("/", "\\")

        # if the name is longer it means that the name is a task or a file
        elif len(splitted_name) > 2:
            # return the def path
            if def_path:
                return os.path.join(
                    self.get_workspace(),
                    app_data["assets"][asset_type]["path"],
                    "_".join([splitted_name[0], splitted_name[1]]),
                    self.get_task_type_from_suffix(splitted_name[2]),
                    "DEF",
                ).replace("/", "\\")

            # return the wip path
            return os.path.join(
                self.get_workspace(),
                app_data["assets"][asset_type]["path"],
                "_".join([splitted_name[0], splitted_name[1]]),
                self.get_task_type_from_suffix(splitted_name[2]),
                "WIP",
            ).replace("/", "\\")

    def get_asset_type_from_prefix(self, prefix):
        """Get the asset type from the prefix.

        :param prefix: The asset prefix
        :type prefix: str

        :return: The asset type. None if found no matching suffix.
        :rtype: str
        """

        app_data = self.db.app_data

        dico = {data["prefix"]: asset for asset, data in app_data["assets"].items()}

        return dico.get(prefix, None)

    def get_task_type_from_suffix(self, suffix):
        """Get the task type from the suffix.

        :param suffix: The asset suffix
        :type suffix: str

        :return: The task type. None if found no matching suffix.
        :rtype: str
        """

        app_data = self.db.app_data

        dico = {data["suffix"]: task for task, data in app_data["tasks"].items()}

        return dico.get(suffix, None)

    def get_informations_from_name(self, name):
        """Figure out the asset information from the full file name.

        :param name: The name to get informations from
        :type name: str

        :return: A tuple of asset_type, basename, task, version, comment, path
        :rtype: tuple
        """
        # split the name to get informations from it
        splitted_name = name.split("_")

        # get the informations
        asset_type = self.get_asset_type_from_prefix(splitted_name[0])
        basename = splitted_name[1]

        if len(splitted_name) == 2:
            path = self.get_path_from_name(name)
            return asset_type, basename, None, None, None, path

        task = self.get_task_type_from_suffix(splitted_name[2])
        if len(splitted_name) == 3:
            path = self.get_path_from_name(name)
            return asset_type, basename, task, None, None, path

        if len(splitted_name) == 4:
            version = int(splitted_name[3].rpartition(".")[0])
            path = self.get_path_from_name(name)
            return asset_type, basename, task, version, None, path

        version = int(splitted_name[3])
        comment = splitted_name[4].rpartition(".")[0]
        if len(splitted_name) > 4:
            path = self.get_path_from_name(name)
            return asset_type, basename, task, version, comment, path

    def get_asset_name(self, asset_type, basename):
        """Get the asset path to the task wip.

        :param asset_type: What type of asset to do (eg: "props", "characters", "shot")
        :type asset_type: str
        :param basename: The asset name
        :type basename: str

        :return: The asset name
        :rtype: str
        """

        app_data = self.db.app_data

        # return the asset name
        return "_".join(
            [
                app_data["assets"][asset_type]["prefix"],
                strings.camel_case(basename, lower_first=True),
            ]
        )

    def get_asset_task_name(self, asset_name, task):
        """Figure out the name of the task from basic informations.

        :param asset_type: What type of asset to do (eg: "props", "characters", "shot")
        :type asset_type: str
        :param asset_name: The asset name with prefix. (eg: "ch_character", "pr_myProp")
        :type asset_name: str
        :param task: What task to create
        :type task: str

        :return: The task file name
        :rtype: str
        """

        app_data = self.db.app_data

        # return the asset name
        return "_".join([asset_name, app_data["tasks"][task]["suffix"]])

    # interact with files

    def open_path(self, name):
        """Open the path to the specifyied asset, task or file.

        :param name: The asset name, task or file
        :type name: str

        :return: The path to the name
        :rtype: str
        """

        # get the path to the file
        path = self.get_path_from_name(name)

        # make sure the path exists before openning it
        if not os.path.exists(path):
            raise ValueError(
                "# Pipeline : The path doesn't seem to exist. "
                + "Make sure to create it before : "
                + path
            )

        # open the path to the file
        subprocess.Popen('explorer "' + path + '"')

        return path

    def get_latest_file(self, directory, extension=None):
        """Get the last alphabetical file in directory.

        :param directory: The directory to look in
        :type directory: str
        :param extension: The file extention to fiter.
            If none, get the latest file of all.
        :type extention: str, none

        :return: The last alphabetical file in the directory. None if directroy is empty
        :rtype: str, none
        """

        # if the directory doesn't exists, abort
        if not os.path.exists(directory):
            return None

        # get all the files that endswith extension in the directory
        content = os.listdir(directory)
        files = list()

        if extension:
            for file in content:
                if file.endswith(extension):
                    files.append(file)
            files = sorted(files)
        else:
            for file in content:
                if os.path.isfile(os.path.join(directory, file)):
                    files.append(file)
            files = sorted(files)

        # if no files were found return none. Else retrun the last alphabetical one.
        if not files:
            return None

        # open the latest file wich is not a bake or finalize file
        for file in list(reversed(files)):
            if not file.endswith("_finalize.ma") and not file.endswith("_bake.ma"):
                origin_file = file
                if os.path.exists(os.path.join(directory, origin_file)):
                    return origin_file

        return files[-1]
