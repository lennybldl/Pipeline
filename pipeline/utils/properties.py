"""Manage properties for the application."""

import json
import os


class DatabaseProperties(object):
    """Manage the data base properties."""

    _app_data = None
    _prefs = None

    def __init__(self):
        # get the current working directories.
        # The number multiplying "../" being the amount of parent directory to ascend
        self.cwd = os.path.abspath(os.path.join(__file__, "../" * 4))
        self.data_path = os.path.join(self.cwd, "data")
        self.app_data_file = os.path.join(self.data_path, "appData.json")
        self.prefs_file = os.path.join(self.data_path, "prefs.json")

    # ---------- manage APP_DATA file
    @property
    def app_data(self):
        """Get the app_data from the app_data.json file.

        :return: All the app_data
        :rtype: dict
        """

        with open(self.app_data_file, "r") as app_data_file:
            return json.load(app_data_file)

    @app_data.setter
    def app_data(self, app_data):
        """Save the app data in a appData.json file.

        :param app_data: The data to save in the file.
        :type app_data: dict
        """

        with open(self.app_data_file, "w") as app_data_file:
            app_data_file.write(json.dumps(app_data, indent=4))

    # ---------- manage PREFS file
    @property
    def prefs(self):
        """Get the preferences from the prefs.json file.

        :return: All the preferences
        :rtype: dict
        """

        with open(self.prefs_file, "r") as prefs_file:
            return json.load(prefs_file)

    @prefs.setter
    def prefs(self, prefs):
        """Save the preferences in the prefs.json file.

        :param prefs: The preferences to save in the file.
        :type prefs: dict
        """

        with open(self.prefs_file, "w") as prefs_file:
            prefs_file.write(json.dumps(prefs, indent=4))
