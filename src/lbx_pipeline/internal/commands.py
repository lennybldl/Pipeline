"""Manage the package's internal commands."""

from lbx_pipeline.internal import logging, session

logger = logging.SessionLogger()


def get_manager():
    """Get the pipeline manager.

    Returns:
        Manager: The pipeline manager.
    """
    if session.MANAGER:
        return session.MANAGER
    logger.error("You first need to start the pipeline")
