"""Manage the application's data."""

import sys

from python_core import logging
from python_core.types import items

from pipeline.internal import config as _config_

# paths in package

PACKAGE_PATH = items.File(__file__).get_upstream(4)
RESOURCES = PACKAGE_PATH.get_folder("resources")
IMAGES = RESOURCES.get_folder("images")
FONTS = RESOURCES.get_folder("fonts")
THEMES = RESOURCES.get_folder("themes")

# static values

STATIC_CONCEPTS = {"global": 0, "asset": 1, "task": 2, "workfile": 3}


class Database(object):
    """Manage the application data."""

    _instance = None  # Database : The database instance.
    software = None  # str : The software we're executing the pipeline from.
    python_version = sys.version_info  # The software's python version.

    _path = None  # str : The documentation path.
    project_name = None  # str : The project's name
    pipeline_path = None  # str : The path to the .pipeline folder.
    config_path = None  # str : The path to the pipeline config.
    rules_path = None  # str : The path to the rules.
    log_path = None  # str : The path to the logs file.

    _config = _config_.Config()  # Config : The config object

    def __new__(cls, software="windows"):
        """Override the __new__ method to always return the same instance.

        Keyword Arguments:
            software (str, optional): The software we're executing the pipeline on.
                Default to "windows".

        Returns:
            Database: An instance of the Database class.
        """
        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
            cls.software = software
            cls.logger = logging.Logger("Pipeline")
        return cls._instance

    # Methods

    def get_path(self):
        """Get the project's path.

        Returns:
            str: The project's path.
        """
        return self._path

    def set_path(self, path):
        """Set the project's path.

        Arguments:
            path (str): The project's path.
        """
        path = items.Folder(path)
        self._path = path
        self.project_name = path.name
        self.pipeline_path = path.get_folder(".pipeline")
        self.config_path = self.pipeline_path.get_file("config.json")
        self.rules_path = self.pipeline_path.get_folder("rules")
        self.log_path = self.pipeline_path.get_file("log.log")

        # set the config path
        self._config.path = self.config_path

    def get_config(self):
        """Get the config from the json file.

        Returns:
            dict: The config.
        """
        return self._config.load()

    def set_config(self, config):
        """Write the new config.

        Arguments:
            config (dict): The dictionnary to write in the config.
        """
        self._config = config
        self._config.dump()

    # Properties

    path = property(get_path, set_path)
    config = property(get_config, set_config)
