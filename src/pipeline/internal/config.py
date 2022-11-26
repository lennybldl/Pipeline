"""Manage the config of the pipeline."""

from python_core.types import dictionaries


class Config(dictionaries.OrderedDictionary):
    """Manage elements of the config."""

    def get_concept_id(self, _id):
        """Get a concept id.

        Arguments:
            _id (int): The id of the concept.

        Returns:
            Concept: The concept as a Concept.
        """
        from pipeline.api import concepts

        return concepts.Concept(_id)

    def get_abstract_step_id(self, _id):
        """Get a abstract step id.

        Arguments:
            _id (int): The id of the abstract step.

        Returns:
            AbstractStep: The step as an AbstractStep.
        """
        from pipeline.api import abstract_steps

        config = self.load()
        _type = config.get("abstracts.id.{}.type".format(_id))
        return abstract_steps.ABSTRACT_STEPS.get(_type)(_id)

    def get_concrete_step_id(self, _id):
        """Get a concrete step id.

        Arguments:
            _id (int): The id of the concrete step.

        Returns:
            ConcreteStep: The step as an ConcreteStep.
        """
        from pipeline.api import concrete_steps

        config = self.load()
        abstract_id = config.get("concretes.id.{}.abstract_id".format(_id))
        _type = config.get("abstracts.id.{}.type".format(abstract_id))
        return concrete_steps.CONCRETE_STEPS.get(_type)(_id)
