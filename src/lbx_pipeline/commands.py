"""Manage the package's commands the artits have access to."""

from lbx_pipeline import manager
from lbx_pipeline.internal import commands


def start(software):
    """Start the pipeline withoud any UI.

    Arguments:
        software (str): The software we're executing the pipeline in.
    """
    manager.Manager(software=software)


# edit project


def load(path):
    """Load a pipeline from a specific path.

    Arguments:
        path (str): The path to the pipeline.
    """
    manager = commands.get_manager()
    if manager:
        manager.load(path)


def create(path):
    """Create the pipeline folder and initialize.

    Arguments:
        path (str): The path to create the pipeline to.
    """
    manager = commands.get_manager()
    if manager:
        manager.create(path)


def save():
    """Save the current pipeline."""
    manager = commands.get_manager()
    if manager:
        manager.project.save()
