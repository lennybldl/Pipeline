"""Manage the config of the pipeline."""

from python_core.types import dictionaries


class Config(dictionaries.OrderedDictionary):
    """Manage elements of the config."""

    def __init__(self, *args, **kwargs):
        """Initialize the config."""

        super(Config, self).__init__(*args, **kwargs)

        from pipeline import api

        self.api = api

    # Methods

    def get_concept_id(self, _id):
        """Get a concept id.

        Arguments:
            _id (int): The id of the concept.

        Returns:
            Concept: The concept as a Concept.
        """
        return self.api.CONCEPT(_id)

    def get_abstract_id(self, _id):
        """Get an abstract step id.

        Arguments:
            _id (int): The id of the abstract step.

        Returns:
            AbstractStep: The step as an AbstractStep.
        """
        config = self.load()
        _type = config.get("abstract.id.{}.type".format(_id))
        return self.api.ABSTRACT_STEPS.get(_type)(_id)

    def get_concrete_id(self, _id):
        """Get a concrete step id.

        Arguments:
            _id (int): The id of the concrete step.

        Returns:
            ConcreteStep: The step as an ConcreteStep.
        """
        config = self.load()
        abstract_id = config.get("concrete.id.{}.abstract_id".format(_id))
        _type = config.get("abstract.id.{}.type".format(abstract_id))
        return self.api.CONCRETE_STEPS.get(_type)(_id)
