"""Manage the concrete steps."""

import os

from python_core.types import dictionaries, strings

from pipeline.api import elements
from pipeline.internal import database

DATABASE = database.Database()


class ConcreteStep(elements.Step):
    """Manage every concrete step of the pipeline."""

    config_path = "concrete.id"

    def add(self, **properties):
        """Add a concrete step to the config."""

        super(ConcreteStep, self).add(**properties)

        # write the path of the step in the config
        config = DATABASE.config
        config.set(
            "concrete.path.{}".format(self.get_path(relative=True)), {"id": self}
        )
        config.dump()

        # log the creation
        DATABASE.logger.debug("Add concrete step. ID : '{}'".format(self))

    def set_properties(self, abstract_id, parent, **kwargs):
        """Write an ordered dictionary of available properties for this step.

        Arguments:
            abstract_id (str): The id of the abstract step this step belongs to.
            parent (int): The id of the parent of this step.

        Returns:
            OrderedDictionary: The ordered dictionary.
        """
        # set the properties
        properties = dictionaries.OrderedDictionary()
        properties["abstract_id"] = abstract_id
        properties["parent"] = parent
        properties["basename"] = kwargs.get("basename", "")
        properties["index"] = kwargs.get("index")
        properties["comment"] = kwargs.get("comment", "")

        return properties

    def get_data(self):
        """Get the concrete and abstract data of the step.

        Returns:
            tuple: The concrete data and the abstract data.
        """
        config = DATABASE.config

        # get the concrete and abstract data of the step
        concrete_data = config.get("{}.{}".format(self.config_path, self))
        abstract_id = concrete_data.get("abstract_id")
        abstract_data = config.get("abstract.id.{}".format(abstract_id))

        return concrete_data, abstract_data

    def get_path(self, relative=False):
        """Get the path of the step.

        Keyword Arguments:
            relative (bool, optional): To get the path relative to the project's path.
                Default to False.

        Returns:
            str: The step's path.
        """
        from pipeline import commands

        def recursively_get_path(_id):
            """Recursively get the name of each parent of a step.

            Arguments:
                _id (int): The step's id.

            Returns:
                _type_: _description_.
            """
            # get useful datas
            concrete_data = commands.get_step_data(_id)[0]

            path = [commands.get_step_name(_id)]
            parent_id = concrete_data.get("parent")
            if parent_id == 0:
                if not relative:
                    path.append(DATABASE.path)
            else:
                path.extend(recursively_get_path(parent_id))

            return path

        # return the formated path
        return os.path.join(*reversed(recursively_get_path(self)))

    def get_name(self):
        """Get the step's name.

        Returns:
            str: The name of the step.
        """
        from pipeline import commands

        # get useful datas
        config = DATABASE.config
        concrete_data, abstract_data = self.get_data()
        name = abstract_data.get("name")

        # process index
        padding = abstract_data.get(
            "index_padding", config.get("abstract.index_padding")
        )
        index = str(concrete_data.get("index")).zfill(padding)

        # process parent name
        parent_name = None
        if "{parent}" in name:
            parent_id = concrete_data.get("parent")
            if parent_id == 0:
                parent_name = DATABASE.project_name
            else:
                parent_name = commands.get_step_name(parent_id)

        # process task name
        task_name = None
        if "{task}" in name:
            parent_id = concrete_data.get("parent")
            if parent_id != 0:
                task_name = commands.get_step_data(parent_id)[1].get("task")

        # process asset name
        asset_name = None
        if "{asset}" in name:
            parent_id = concrete_data.get("parent")
            while True:
                # if the step is child of the root it can not have a parent asset
                if parent_id == 0:
                    asset_name = None
                    break
                # get the parent asset
                parent_concrete_data, parent_abstract_data = commands.get_step_data(
                    parent_id
                )
                if parent_abstract_data.get("type") == "asset":
                    asset_name = commands.get_step_name(parent_id)
                    break
                parent_id = parent_concrete_data.get("parent")

        # match the variables and the values to replace them with
        match = {
            "{project}": DATABASE.project_name,
            "{parent}": parent_name,
            "{asset}": asset_name,
            "{task}": task_name,
            "{basename}": concrete_data.get("basename"),
            "{index}": index,
            "{comment}": concrete_data.get("comment"),
            "{extension}": concrete_data.get("extension"),
        }

        # replace the variables in the path with the matching values
        # and get rid of double underscores
        name = strings.replace(abstract_data.get("name"), match.keys(), match.values())
        while "__" in name:
            name = name.replace("__", "_")
        return name

    def get_rules(self):
        """Override the get_rules methods to get the rules from the abstract id.

        Returns:
            dict: A dictionary of rules.
        """
        config = DATABASE.config
        abstract_id = config.get_abstract_id(self.abstract_id)
        return abstract_id.get_rules()


class ConcreteAsset(ConcreteStep):
    """Manage every concrete asset of the pipeline."""


class ConcreteTask(ConcreteStep):
    """Manage every concrete task of the pipeline."""


class ConcreteWorkfile(ConcreteStep):
    """Manage every concrete workfile of the pipeline."""
