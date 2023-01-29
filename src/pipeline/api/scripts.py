"""Manage the scripts."""

import os
import sys

from python_core.types import items

from pipeline.internal import core


class Script(items.File):
    """Manage a script object."""


class PythonScript(Script):
    """Manage a python script object."""

    def call(self, *args, **kwargs):
        """Call the pyhton script by executing the execute function of the script."""

        if not self.exists():
            core.LOGGER.warning(
                "The script doesn't exist and cannot be called - '{}'".format(self)
            )
            return

        # import the module in a different way depending on the python version
        if core.MANAGER.python_version[0] == 2:
            import imp

            module = imp.load_source(self.name, self.path)
        else:
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                self.name.replace(".py", ""), self.path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

        # execute the module
        if hasattr(module, "execute"):
            try:
                module.execute(*args, **kwargs)
            except:  # noqa E722
                core.PROJECT_LOGGER.exception(
                    "An error occured while executing - '{}'".format(self)
                )
        else:
            core.PROJECT_LOGGER.warning(
                "Could not find an 'execute' function in - '{}'".format(self)
            )


class ProjectPythonScript(PythonScript):
    """Manage a project python script object."""

    def __init__(self, path, *args, **kwargs):
        """Initialize the script.

        Arguments:
            path (str): The path of the script.
                If the path is relative, make it relative
                to the project's commands folder.
        """
        # get the path of the script, relative to the project's commands folder
        if os.path.isabs(path) or not os.path.exists(path):
            path = os.path.join(core.MANAGER.commands_path, path)

        # initialize the pyton script
        super(ProjectPythonScript, self).__init__(path, *args, **kwargs)

    # methods

    def create(self):
        """Create the script if it doesn't exist."""
        if not self.exists():
            # create the drectory that stores the script
            if not self.directory.exists():
                self.directory.create()

            # create the default script
            default_command = core.APP_RESOURCES.get_file("default_command.py")
            content = default_command.read()
            base_name = self.base_name
            self.write(content.format(name=base_name, title=base_name.title()))

    def call(self, member, *args, **kwargs):
        """Call the pyhton script by executing the execute function of the script.

        Arguments:
            member (Member): The member to execute the script on.
        """
        super(ProjectPythonScript, self).call(member, *args, **kwargs)

    # properties

    @property
    def relative_path(self):
        """Get the path of the script relative to the commands path.

        Returns:
            str: The relative path.
        """
        return self.relative_to(core.MANAGER.commands_path)
