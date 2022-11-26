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

    def get_theoretical_step_id(self, _id):
        """Get a theoretical step id.

        Arguments:
            _id (int): The id of the theoretical step.

        Returns:
            TheoreticalStep: The step as an TheoreticalStep.
        """
        from pipeline.api import theoretical_steps

        config = self.load()
        _type = config.get("theoreticals.id.{}.type".format(_id))
        return theoretical_steps.ABSTRACT_STEPS.get(_type)(_id)

    def get_concrete_step_id(self, _id):
        """Get a concrete step id.

        Arguments:
            _id (int): The id of the concrete step.

        Returns:
            ConcreteStep: The step as an ConcreteStep.
        """
        from pipeline.api import concrete_steps

        config = self.load()
        theoretical_id = config.get("concretes.id.{}.theoretical_id".format(_id))
        _type = config.get("theoreticals.id.{}.type".format(theoretical_id))
        return concrete_steps.CONCRETE_STEPS.get(_type)(_id)
