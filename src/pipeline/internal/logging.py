"""Manage the application's logs."""

from python_core import logging


class Logger(logging.Logger):
    """Manage the application logs."""


class ProjectLogger(Logger):
    """Manage the current pipeline project logs."""

    _instance = None  # ProjectLogger : The logger instance.

    def __new__(cls):
        """Override the __new__ method to always return the same instance.

        Returns:
            ProjectLogger: An instance of the Logger class.
        """
        if not cls._instance:
            cls._instance = super(ProjectLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        """Initialize the logger."""

        super(ProjectLogger, self).__init__("Pipeline Project", *args, **kwargs)
