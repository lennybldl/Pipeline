"""Manage the application's logs."""

from lbx_python_core import logging

import lbx_pipeline


class Logger(logging.Logger):
    """Manage the application logs."""


class SessionLogger(Logger):
    """Manage the current session pipeline logs."""

    _instance = None  # SessionLogger : The logger instance.

    def __new__(cls):
        """Override the __new__ method to always return the same instance.

        Returns:
            SessionLogger: An instance of the Logger class.
        """
        if not cls._instance:
            cls._instance = super(SessionLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self, *args, **kwargs):
        """Initialize the logger."""

        super(SessionLogger, self).__init__(
            "({}) SESSION".format(lbx_pipeline.NAME), *args, **kwargs
        )
