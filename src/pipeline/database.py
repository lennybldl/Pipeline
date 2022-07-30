"""Manage the application's data."""

from python_core import logging
from python_core.types import items, dictionaries

# paths in package

PACKAGE_PATH = items.File(__file__).get_upstream(3)
RESSOURCES = PACKAGE_PATH.get_folder("ressources")

# static values

STATIC_CONCEPTS = {"global": 1, "asset": 2, "task": 3, "workfile": 4}


class Database(object):
    """Manage the application data."""

    _instance = None  # str : The database instance.
    software = None  # str : The software we're executing the pipeline from.
    py_version = None  # int : The python version used by the software we're in.

    _path = None  # str : The documentation path.
    project_name = None  # str : The project's name
    pipeline_path = None  # str : The path to the .pipeline folder.
    config_path = None  # str : The path to the pipeline config.
    rules_path = None  # str : The path to the rules.
    log_path = None  # str : The path to the logs file.

    def __new__(cls, software, py_version):
        """Override the __new__ method to always return the same instance.

        Arguments:
            software (str): The software we're executing the pipeline on.
            py_version (int): The python version used by the software we're in.

        Returns:
            Database: An instance of the Database class.
        """

        if not cls._instance:
            cls._instance = super(Database, cls).__new__(cls)
            cls.software = software
            cls.py_version = py_version
            cls.logger = logging.Logger("Pipeline")
        return cls._instance

    # methods

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

    def get_config(self):
        """Get the config from the json file.

        Returns:
            dict: The config.
        """

        config = dictionaries.OrderedDictionary()
        config.path = self.config_path
        return config.load()

    def set_config(self, config):
        """Write the new config.

        Arguments:
            config (dict): The dictionnary to write in the config.
        """
        config_dict = dictionaries.OrderedDictionary(config)
        config_dict.dump(self.config_path)

    # properties

    path = property(get_path, set_path)
    config = property(get_config, set_config)
