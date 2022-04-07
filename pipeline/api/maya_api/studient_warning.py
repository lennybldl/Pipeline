"""Get rid of the studient warning on maya files."""

import os
from pipeline.api.assets import paths


def remove_from_file(file):
    """Remove the studient warning from a specific file.

    :param file: The complete file path to the .ma file
        to remove the studient warnign from.
    :type file: str
    """

    # get the file lines
    with open(file, "r") as maya_file:
        lines = maya_file.readlines()

    # look for the studient warning
    for line in lines:
        if 'fileInfo "license" "student";' in line:
            break
    lines.remove(line)

    # re_write the file
    with open(file, "w") as maya_file:
        maya_file.write("".join(lines))

    print("# Pipeline : Studient warning removed from -> " + file)


def remove_from_all_files(folders=None):
    """Remove the studient warning from all the .ma files.

    :param folders: If none : modify every .ma files in the workspace.
        If folders : modify files that are in folders that ends with an item of the list
    :type folders: list, none
    """

    # manage the paths
    _paths = paths.Paths()

    for root, dirs, project_files in os.walk(_paths.get_workspace(), topdown=True):
        # remove studient warning from maya files that are in folders
        if folders:
            for maya_file in project_files:
                if maya_file.endswith(".ma"):
                    for folder in folders:
                        if root.endswith(folder):
                            remove_from_file(os.path.join(root, maya_file))

        # remove studient warning from all the maya files
        else:
            for maya_file in project_files:
                if maya_file.endswith(".ma"):
                    remove_from_file(os.path.join(root, maya_file))
