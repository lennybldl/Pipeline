"""Execute the script from maya."""

from maya import OpenMayaUI as oMui
from PySide2.QtWidgets import QMainWindow
from shiboken2 import wrapInstance
from python_core.pyside2.config import config

from pipeline.ui import main, theme
from pipeline.utils import database, maya_config


def maya_main_window():
    """Get the maya's QMainWindow object.

    :return: maya's QMainWindow object
    :rtype: QMainWindow
    """

    return wrapInstance(int(oMui.MQtUtil.mainWindow()), QMainWindow)


def exec_():
    """Execute the application."""

    # Make sure the application runs on safe basis
    db = database.Database()
    db.start_checks()

    # get the project path
    maya_config.get_project_path()

    # display tooltips to have informations on items
    config.set("debug.show_tooltip", False)

    # create the window
    window = main.Main(maya_main_window())
    window.window_size = (300, 600)
    window.populate()
    theme.theme(window)
    window.show()

    return window
