"""Manage the classes that control every member of the pipeline."""

from python_core.types import dictionaries

from pipeline.internal import database

DATABASE = database.Database()


class Member(int):
    """Manage every member of the pipeline."""

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

    # methods

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
                for member in values:
                    if isinstance(member, str):
                        member = config.get_concept_id(member.replace("c", ""))
                    else:
                        member = config.get_theoretical_step_id(member)
                    rules.update(member.get_rules())
            # get the rules of the current step
            else:
                rules[rule_name] = values
        return rules

    def get_properties(self):
        """Get all the properties saved in the config.

        Returns:
            dict: All the properties.
        """
        return DATABASE.config.get("{}.{}".format(self.config_path, self))


class Step(Member):
    """Manage every step of the pipeline."""

    def add(self, **properties):
        """Add a step to the config."""
        config = DATABASE.config

        # set the properties
        properties = self.set_properties(**properties)

        # write the new config
        config.set("{}.{}".format(self.config_path, self), properties)
        config.dump()
