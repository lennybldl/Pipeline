"""Manage the main window of the application."""

import functools

from PySide2.QtGui import QFontDatabase
from PySide2.QtWidgets import QStyleFactory
from python_core.pyside2 import base_ui

import pipeline
from pipeline import commands
from pipeline.internal import database
from pipeline.ui.internal import themes
from pipeline.ui.tabs import design_tab


IMAGES = database.IMAGES


class AbstractMainWindow(base_ui.MainWindow):
    """Only meant for inheritance manage the abstract behaviours of the main window."""

    _title = "Pipeline - {}".format(pipeline.VERSION)
    _icon = IMAGES.get_file("pipe.png")

    _theme = "dark"

    def __init__(self, *args, **kwargs):
        """Initialize the main window."""
        super(AbstractMainWindow, self).__init__(*args, **kwargs)
        self.import_fonts()
        self.set_theme(self.theme)
        self.build_ui()

    def build_ui(self):
        """Build the widget's UI"""

        menu_bar = self.layout.add_menu_bar(parent=self)
        menu_bar.setFixedHeight(30)
        # add a file menu
        file_menu = menu_bar.add_menu("File")
        file_menu.add_action(
            "New pipeline", triggered=self.create_pipeline, shortcut="CTRL+N"
        )
        file_menu.add_action(
            "Open pipeline", triggered=self.open_pipeline, shortcut="CTRL+O"
        )
        # add an edit menu
        edit_menu = menu_bar.add_menu("Edit")
        themes_menu = edit_menu.add_menu("Themes")
        for theme in database.THEMES.folders():
            theme = theme.name
            themes_menu.add_action(
                theme, triggered=functools.partial(self.set_theme, theme)
            )

        # create the widgets to store in the tabs
        design_tab_widget = design_tab.DesignTab()

        # create the tab widget
        tab_widget = self.layout.add_tab_widget()
        tab_widget.add_tab("Design", widget=design_tab_widget)
        tab_widget.add_tab("Project")

        # keep the tabs in memory
        self.tabs = [design_tab_widget]

    # methods

    def sync(self):
        """Synchronize the widget with the rest of the UI"""

        for tab in self.tabs:
            tab.sync()

    def import_fonts(self):
        """Import the accessable fonts for the application."""

        for font in database.FONTS.files():
            QFontDatabase.addApplicationFont(font)

    def get_theme(self):
        """theme.

        Returns:
            str: The name of the theme.
        """
        return self._theme

    def set_theme(self, theme):
        """Set the main window theme.

        Arguments:
            theme (str): The name of the theme.
        """
        # set the theme
        theme = themes.Theme(theme)
        self.style_sheet = theme.style_sheet
        self.setStyle(QStyleFactory.create(theme.get("style_factory")))

        # save the current theme
        self._theme = theme

    # properties

    theme = property(get_theme, set_theme)

    # signals

    def create_pipeline(self):
        """Create a new pipeline."""

        # browse to a path to create the pipeline in
        dialog = base_ui.BrowseDialog(title="Select a path to create a new pipeline")
        paths = dialog.browse(to_file=False)

        # create the pipeline
        if paths:
            commands.create_pipeline(paths[0])
            self.sync()

    def open_pipeline(self):
        """Load an existing pipeline."""

        # browse to the pipeline's path
        dialog = base_ui.BrowseDialog(title="Select the path of a pipeline to open")
        paths = dialog.browse(to_file=False)

        if paths:
            commands.initialize(paths[0])
            self.sync()


class WindowsMainWindow(AbstractMainWindow):
    """Manage the main window for windows."""

    _window_size = (800, 800)
