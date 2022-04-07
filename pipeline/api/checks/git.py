"""Manage the checks fo git publishes."""

import os

from pipeline.api.assets import paths
from pipeline.utils import units

PATHS = paths.Paths()


def _get_gitignore_content():
    """Get the gitignore content.

    :return: The gitignore content as a list.
    :rtype: list
    """

    # get the current workspace to get relatives paths
    workspace = PATHS.get_workspace()

    # get the current state of gitignore
    path = os.path.join(workspace, ".gitignore")

    gitignore = list()
    if os.path.exists(path):
        with open(path, "r") as gitignore_file:
            lines = gitignore_file.readlines()

            # get rig of jumped lines
            for line in lines:
                if line != "\n":
                    gitignore.append(line.replace("\n", ""))

    return gitignore


def _write_gitignore(content):
    """Write the gitignore file with a new content.

    :param content: The content to write in the gitignore file.
    :type content: str
    """

    # get the current workspace to get relatives paths
    workspace = PATHS.get_workspace()

    # get the current state of gitignore
    path = os.path.join(workspace, ".gitignore")

    with open(path, "w") as gitignore_file:
        gitignore_file.write(content)


def update_gitignore():
    """Update the gitignore file to ignore the WIPs folders."""

    # get the current workspace to get relatives paths
    workspace = PATHS.get_workspace()

    # get the current gitignore content
    gitignore = _get_gitignore_content()

    # check every folders and make sure no WIP folder will be pushed
    for root, dirs, files in os.walk(workspace, topdown=True):
        # add WIP folders to gitignore
        if root.endswith("\\WIP"):
            root = root.replace(workspace, "").replace("\\", "/") + "/"
            if root not in gitignore:
                gitignore.append(root)

    # write the new gitignore
    _write_gitignore("\n".join(sorted(gitignore)))

    print("# Pipeline : .gitignore updated")


def ignore_oversized_files():
    """Github only allows files below 100MB.

    Add every files larger than that to the gitignore.
    """

    # get the current workspace to get relatives paths
    workspace = PATHS.get_workspace()

    # get the current gitignore content
    gitignore = _get_gitignore_content()

    # check every folders and make sure no oversized files will be pushed
    for root, dirs, files in os.walk(workspace, topdown=True):
        # skip files with WIP in their name
        if "\\WIP\\" not in root.replace(workspace, ""):
            for file in files:
                stats = os.stat(os.path.join(root, file))
                size, unit = units.convert_byte(stats.st_size)

                if size >= 99.9 and unit not in ["B", "KB"]:
                    file = os.path.join(root, file)
                    file = file.replace(workspace, "").replace("\\", "/")

                    if file not in gitignore:
                        gitignore.append(file)

                        print(
                            "# Pipeline : {} added to .gitignore ".format(file)
                            + "because it was to large. (~ {} {})".format(size, unit)
                        )

    # write the new gitignore
    _write_gitignore("\n".join(sorted(gitignore)))
