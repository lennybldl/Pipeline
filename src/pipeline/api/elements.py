"""Manage the classes that control every element of the pipeline."""

from python_core.types import dictionaries

from pipeline.internal import database

DATABASE = database.Database()


class Element(int):
    """Manage every element of the pipeline."""

    config_path = None  # str : The path to the config

    def __getattribute__(self, name):
        """Override the __getattribute__ method.

        Arguments:
            name (str): The name of the attribute to get.

        Returns:
            -: The attribute.
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return DATABASE.config.get("{}.{}.{}".format(self.config_path, self, name))

    # Methods

    def get_rules(self):
        """Get the rules that can be performed on the step.

        Returns:
            dict: A dictionary of rules.
        """
        config = DATABASE.config

        rules = dictionaries.OrderedDictionary()
        for rule_name, values in self.rules.items():
            # get the rules from an other step rules
            if rule_name == "_same_as_":
                for element in values:
                    if isinstance(element, str):
                        element = config.get_concept_id(element.replace("c", ""))
                    else:
                        element = config.get_abstract_id(element)
                    rules.update(element.get_rules())
            # get the rules of the current step
            else:
                rules[rule_name] = values
        return rules


class Concept(Element):
    """Manage every concept of the pipeline."""

    config_path = "concept.id"

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


class Step(Element):
    """Manage every step of the pipeline."""

    def add(self, **properties):
        """Add a step to the config."""
        config = DATABASE.config

        # set the properties
        properties = self.set_properties(**properties)

        # write the new config
        config.set("{}.{}".format(self.config_path, self), properties)
        config.dump()
