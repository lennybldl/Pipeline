"""Manage the themes for the application."""

from python_core.pyside2.internal import style_sheets
from python_core.types import dictionaries, strings

from pipeline.internal import database

THEMES = database.THEMES


class Theme(dictionaries.Dictionary):
    """Manage the theme class."""

    theme = dict()
    theme_folder = None

    def __init__(self, theme, *args, **kwargs):
        """Initialize the theme.

        Arguments:
            theme (str): The name of the theme.
        """
        # get the theme path from its name
        self.theme_folder = THEMES.get_folder(theme)
        theme_file = self.theme_folder.get_file("theme.json")

        # read the dictionary
        super(Theme, self).__init__(theme_file, *args, **kwargs)

        # process the theme
        self.process_theme()

    # methods

    def process_theme(self):
        """Process the theme to get the style sheet.

        Returns:
            str: The processed style sheet as a string.
        """
        # get the variables
        variables = self.get("colors")
        for image in self.get("images"):
            variables[image] = self.theme_folder.get_file(image).slashed()

        # get the style sheet
        theme = dictionaries.dumps(self.get("theme"))
        theme = strings.replace(
            theme,
            elements=["{" + key + "}" for key in variables.keys()],
            by=variables.values(),
        )
        theme = self.loads(theme, object_pairs_hook=None)
        self.style_sheet = style_sheets.dict_to_style_sheet(theme)

        return self.style_sheet
