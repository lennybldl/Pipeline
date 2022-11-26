"""Manage the concepts."""

from python_core.types import dictionaries

from pipeline.api import members
from pipeline.internal import database

DATABASE = database.Database()


class Concept(members.Member):
    """Manage every concept of the pipeline."""

    config_path = "concepts.id"

    def add(self, name, **kwargs):
        """Add this specific concept to the config.

        Arguments:
            name (str): The name to give to the concept.
        """
        config = DATABASE.config

        # set default values for the concept
        properties = dictionaries.OrderedDictionary()
        properties["name"] = name
        properties["rules"] = kwargs.get("rules", {"_same_as_": list()})

        # write the new config
        config.set("{}.{}".format(self.config_path, self), properties)
        config.dump()

        # log the creation
        DATABASE.logger.debug("Add concept. ID : '{}'".format(self))
