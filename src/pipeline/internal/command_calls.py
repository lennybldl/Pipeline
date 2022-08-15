"""Manage the way project commands are called."""

import sys

from pipeline.internal import database

DATABASE = database.Database(software="windows", py_version=3)

# Use different modules to import modules considering the python version
if DATABASE.py_version == 2:
    import imp
else:
    import importlib.util


def call_python_command(command, _id):
    """Execute a python command.

    Arguments:
        command (str): The path to the command, relative to the rules path.
        _id (int): The id of the concrete step.
    """
    command = DATABASE.rules_path.get_file(command)

    # import the module
    if DATABASE.py_version == 2:
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
            DATABASE.logger.exception(
                "An error occured while executing '{}'".format(command)
            )
    else:
        DATABASE.logger.warning(
            "Could not find an 'execute' function in '{}'".format(command)
        )
