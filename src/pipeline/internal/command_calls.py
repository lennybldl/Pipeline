"""Manage the way project commands are called."""

import sys

from pipeline.internal import manager

MANAGER = manager.Manager()

# Use different modules to import modules considering the python version
if MANAGER.python_version[0] == 2:
    import imp
else:
    import importlib.util


def call_python_command(command, _id):
    """Execute a python command.

    Arguments:
        command (str): The path to the command, relative to the rules path.
        _id (int): The id of the concrete step.
    """
    command = MANAGER.rules_path.get_file(command)

    # import the module
    if MANAGER.python_version[0] == 2:
        module = imp.load_source(command.name, command.path)
    else:
        spec = importlib.util.spec_from_file_location(
            command.name.replace(".py", ""), command.path
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

    # execute the module
    if hasattr(module, "execute"):
        try:
            module.execute(_id)
        except:  # noqa E722
            MANAGER.logger.exception(
                "An error occured while executing '{}'".format(command)
            )
    else:
        MANAGER.logger.warning(
            "Could not find an 'execute' function in '{}'".format(command)
        )
