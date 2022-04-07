"""Actions to perform if app launched from maya."""

from maya import cmds

from pipeline.utils import database

DATABASE = database.Database()


def get_project_path():
    """Get the maya project path."""

    prefs = DATABASE.prefs

    prefs.update({"workspace": cmds.workspace(q=True, rootDirectory=True)})

    DATABASE.prefs = prefs
