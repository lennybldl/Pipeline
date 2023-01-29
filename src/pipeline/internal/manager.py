"""Manage the application."""

import sys

from python_core.types import items

from pipeline.internal import core


class Manager(object):
    """Manage the application."""

    _instance = None  # Manager : The manager instance.
    software = None  # str : The software we're executing the pipeline from.
    python_version = sys.version_info  # The software's python version.

    _path = None  # str : The documentation path.
    project_name = None  # str : The project's name
    pipeline_path = None  # str : The path to the .pipeline folder.
    project_path = None  # str : The path to the pipeline project.
    commands_path = None  # str : The path to the commands.
    log_path = None  # str : The path to the logs file.

    def __new__(cls, software="windows"):
        """Override the __new__ method to always return the same instance.

        Keyword Arguments:
            software (str, optional): The software we're executing the pipeline on.
                Default to "windows".

        Returns:
            Manager: An instance of the Manager class.
        """
        if not cls._instance:
            cls._instance = super(Manager, cls).__new__(cls)
            cls.software = software

            # make the manager able to manage a project
            from pipeline.api import project as _project

            cls.project = _project.Project()  # Project : The project object

        return cls._instance

    # methods

    def load_project(self, path):
        """Load a pipeline from a specific path.

        Arguments:
            path (str): The path to the project.
        """
        # create the .pipeline folder if it doesn't exist
        path = items.Folder(path)
        if not path.get_folder(".pipeline").exists():
            core.LOGGER.warning("The path doesn't exist.")
            return

        # load the pipeline project
        self.path = path
        core.PROJECT_LOGGER.add_file_handler(self.log_path, mode="w")

    def create_project(self, path):
        """Create the pipeline folder and initialize.

        Arguments:
            path (str): The path to create the pipeline to.
        """
        # get if the project already exists
        project_path = items.Folder(path)
        if project_path.exists():
            return

        # create the project folder
        project_path.create()

        # create the pipeline folder for the project
        pipeline_path = core.RESOURCES.get_folder(".pipeline")
        pipeline_path.copy(to=project_path.get_folder(".pipeline"))

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
        self.project_path = self.pipeline_path.get_file("project.json")
        self.commands_path = self.pipeline_path.get_folder("commands")
        self.log_path = self.pipeline_path.get_file("log.log")

        # set the project path
        self.project.path = self.project_path
        self.project.load()

    # properties

    path = property(get_path, set_path)
