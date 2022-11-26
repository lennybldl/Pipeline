"""Manage the ui of the pipeline."""

from pipeline import commands
from pipeline.ui import main_window
from PySide2.QtWidgets import QApplication


def launch_windows_ui():
    """Launch the UI on a windows device.

    Returns:
        WindowsMainWindow: The created main window.
    """
    commands.start(software="windows")

    app = QApplication()
    window = main_window.WindowsMainWindow()
    window.show()
    app.exec_()

    return window
