"""Manage the abstract steps."""

import os

from python_core.types import dictionaries

from pipeline.api import elements
from pipeline.internal import database

DATABASE = database.Database()


class AbstractStep(elements.Step):
    """Manage every abstract step of the pipeline."""

    _type = None
    config_path = "abstract.id"

    def add(self, **properties):
        """Add an abstract step to the config."""

        super(AbstractStep, self).add(**properties)

        # log the creation
        DATABASE.logger.debug("Add abstract step. ID : '{}'".format(self))

    def set_properties(self, parent, **kwargs):
        """Write an ordered dictionary of available properties for this step.

        Arguments:
            parent (int): The id of the parent of this step.

        Returns:
            OrderedDictionary: The ordered dictionary.
        """
        # get useful values
        concept = kwargs.get("concept", database.STATIC_CONCEPTS.get(self._type))

        # set the properties
        properties = dictionaries.OrderedDictionary()
        properties["type"] = self._type
        properties["name"] = kwargs.get(
            "name", "{}{}".format(self._type, self) + "_{index}"
        )
        properties["parent"] = parent
        properties["concept"] = concept
        # add the rules for the abstract step
        properties["rules"] = kwargs.get(
            "rules", {"_same_as_": ["c{}".format(concept)]}
        )

        return properties

    def get_abstract_path(self, relative=True):
        """Get the abstract path of the abstarct step.

        Keyword Arguments:
            relative (bool, optional): To get the path relative to the project's path.
                Default to True.

        Returns:
            str: The unformated procedural path of the abstract step.
        """
        config = DATABASE.config

        step_path = [DATABASE.path]
        parent_id = self
        while True:
            step_path.insert(-1, config.get("abstract.id.{}.name".format(parent_id)))
            parent_id = config.get("abstract.id.{}.parent".format(parent_id))
            if parent_id == 0:
                break

        # ignore the project path if we want a relative path
        if relative:
            step_path.pop(-1)

        return os.path.join(*reversed(step_path))


class AbstractAsset(AbstractStep):
    """Manage every abstract asset of the pipeline."""

    _type = "asset"


class AbstractTask(AbstractStep):
    """Manage every abstract task of the pipeline."""

    _type = "task"

    def set_properties(self, **kwargs):
        """Write an ordered dictionary of available properties for this step.

        Returns:
            OrderedDictionary: The ordered dictionary.
        """
        # set the properties
        properties = super(AbstractTask, self).set_properties(**kwargs)
        properties["task"] = kwargs.get("task", "task{}".format(self))
        properties.move_to_end("rules")
        return properties


class AbstractWorkfile(AbstractStep):
    """Manage every abstract workfile of the pipeline."""

    _type = "workfile"
