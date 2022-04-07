"""Manage images."""

import os


def get(name):
    """Get the image path from name

    :param name: The name of the image
    :type name: str
    """

    return os.path.join(os.path.dirname(__file__), name).replace("\\", "/")
