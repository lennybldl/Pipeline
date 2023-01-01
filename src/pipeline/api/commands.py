"""Manage the commands of the project."""

from python_core.types import signals

from pipeline.api import scripts
from pipeline.internal import manager


class Command(list):
    """Manage the command."""

    def __init__(self, name, _scripts=None):
        """Initialize the command.

        Arguments:
            name (str): The name of the command.
        """
        # create signals
        self.has_been_edited = signals.Signal()

        # initialize the command
        self.name = name
        _scripts = [scripts.ProjectPythonScript(o) for o in _scripts or list()]
        super(Command, self).__init__(_scripts)

    # methods

    def append(self, other):
        """Append a project script to the current command.

        Arguments:
            other (str): The script to append.
        """
        super(Command, self).append(scripts.ProjectPythonScript(other))
        self.has_been_edited.emit()

    def extend(self, others):
        """Extend a list of project scripts to the current command.

        Arguments:
            others (str): The list of scripts to extend.
        """
        super(Command, self).extend([scripts.ProjectPythonScript(o) for o in others])
        self.has_been_edited.emit()

    def call(self, member, *args, **kwargs):
        """Call the command by executing all its scripts.

        Arguments:
            member (Member): The member to execute the command on.
        """
        manager.LOGGER.info(
            "Call '{}' command on member '{}'".format(
                self.name, member.full_project_path
            )
        )

        # call each script
        for script in self:
            script.call(member, *args, **kwargs)

        manager.LOGGER.debug("'{}' done".format(self.name))
