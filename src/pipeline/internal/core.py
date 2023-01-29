"""Manage the constant variables of the application."""

from python_core.types import items

from pipeline.internal import logging

# paths in package
PACKAGE_PATH = items.File(__file__).get_upstream(4)
RESOURCES = PACKAGE_PATH.get_folder("resources")
IMAGES = RESOURCES.get_folder("images")
FONTS = RESOURCES.get_folder("fonts")
THEMES = RESOURCES.get_folder("themes")
APP_RESOURCES = RESOURCES.get_folder("app_resources")

# a manager variable to acces the same instance for all the application
MANAGER = None

# the loggers of the application
LOGGER = logging.Logger("Pipeline Manager")
PROJECT_LOGGER = logging.ProjectLogger()

# properties visibility
PUBLIC = "public"
PROTECTED = "protected"
PRIVATE = "private"
VISIBILITY_MODES = [PUBLIC, PROTECTED, PRIVATE]

# properties
STICKY_PROPERTIES = ("super_member", "sub_members")
