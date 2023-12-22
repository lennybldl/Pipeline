"""Manage the application."""

from lbx_pipeline.internal import session


class Manager(object):
    """Manage the application."""

    _instance = None  # Manager : The manager instance.
    software = None  # str : The software we're executing the pipeline from.

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
            session.MANAGER = cls._instance

        return cls._instance

    # methods

    def load(self, path):
        """Load a pipeline from a specific path.

        Arguments:
            path (str): The path to the project.
        """

    def create(self, path):
        """Create the pipeline folder and initialize.

        Arguments:
            path (str): The path to create the pipeline to.
        """
