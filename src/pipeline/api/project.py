"""Manage the project of the pipeline."""

from python_core.types import dictionaries, signals

from pipeline.api import abstract_steps, concepts, concrete_steps
from pipeline.internal import logging


LOGGER = logging.ProjectLogger()


class Project(dictionaries.Dictionary):
    """Manage elements of the project."""

    def __init__(self, *args, **kwargs):
        """Initialize the project."""

        # create signals
        self.has_been_edited = signals.Signal()

        # initialize the object
        super(Project, self).__init__(*args, **kwargs)

    # global methods

    def load(self, *args, **kwargs):
        """Load the project."""
        super(Project, self).load(*args, **kwargs)
        # keep some global properties in memory
        self.properties_order = self.get("global.properies_order")

    def save(self):
        """Save the current project pipeline."""
        self.dump()
        LOGGER.info("Save")

    # add members

    def add_member(self, member):
        """Add a member to the project and write it."""
        # save the member in its serialized form
        self.set("{}.{}".format(member.project_path, member._id), member.serialize())

        # connect the member has_been_edited signal to the project signal
        member.has_been_edited.connect(self.has_been_edited.emit)

    def add_concept(self, *args, **kwargs):
        """Add a concept to the project.

        Returns:
            Concept: The added concept.
        """
        # create the concept
        _id = self.get_available_concept_id()
        member = concepts.Concept(_id, *args, **kwargs)
        self.add_member(member)

        # log the creation
        LOGGER.debug("Add concept. ID : '{}'".format(_id))

        return member

    def add_abstract_step(self, *args, **kwargs):
        """Add a abstract step to the project.

        Returns:
            AbstractStep: The added abstract step.
        """
        # create the abstract step
        _id = self.get_available_abstract_id()
        member = abstract_steps.AbstractStep(_id, *args, **kwargs)
        self.add_member(member)

        # log the creation
        LOGGER.debug("Add abstract step. ID : '{}'".format(_id))

        return member

    def add_concrete_step(self, *args, **kwargs):
        """Add a concrete step to the project.

        Arguments:
            abstract_step (str): The id of the abstract step this step belongs to.

        Returns:
            ConcreteStep: The concrete step.
        """
        # create the concrete step
        _id = self.get_available_concrete_id()
        member = concrete_steps.ConcreteStep(_id, *args, **kwargs)
        self.add_member(member)

        # log the creation
        LOGGER.debug("Add concrete step. ID : '{}'".format(_id))

        return member

    # get members

    def get_member(self, path):
        """Get a member from the project.

        Arguments:
            path (str): A dot separated path to the member.

        Returns:
            Member: The desired member.
        """
        path, _, _id = path.rpartition(".")
        if "concept" in path:
            return self.get_concept(_id)
        elif "abstract" in path:
            return self.get_abstract_step(_id)
        elif "concrete" in path:
            return self.get_concrete_step(_id)

        return None

    def get_concept(self, _id):
        """Get a concept id.

        Arguments:
            _id (int): The id of the concept.

        Returns:
            Concept: The concept as a Concept.
        """
        # get the member
        member = concepts.Concept(_id=_id)
        # connect the member's signals
        member.has_been_edited.connect(self.has_been_edited.emit)
        return member

    def get_abstract_step(self, _id):
        """Get a abstract step id.

        Arguments:
            _id (int): The id of the abstract step.

        Returns:
            AbstractStep: The step as an AbstractStep.
        """
        return abstract_steps.AbstractStep(_id=_id)

    def get_concrete_step(self, _id):
        """Get a concrete step id.

        Arguments:
            _id (int): The id of the concrete step.

        Returns:
            ConcreteStep: The step as an ConcreteStep.
        """
        return concrete_steps.ConcreteStep(_id=_id)

    def list_concepts(self):
        """List all the existing concepts.

        Returns:
            list: A list of concept members.
        """
        return [self.get_concept(_id) for _id in self.get("concept.id").keys()]

    def list_abstract_steps(self):
        """List all the existing abstract_steps.

        Returns:
            list: A list of abstract_step members.
        """
        return [self.get_abstract_step(_id) for _id in self.get("abstract.id").keys()]

    def list_concrete_steps(self):
        """List all the existing concrete_steps.

        Returns:
            list: A list of concrete_step members.
        """
        return [self.get_concrete_step(_id) for _id in self.get("concrete.id").keys()]

    # get available ids

    def get_available_concept_id(self):
        """Get the next available concept id.

        Returns:
            int: The available id.
        """
        existing_ids = list(map(int, self.get("concept.id").keys()))
        potential_ids = set(range(1, len(existing_ids) + 2))
        return list(potential_ids - set(existing_ids))[0]

    def get_available_abstract_id(self):
        """Get the next available abstract id.

        Returns:
            int: The available id.
        """
        existing_ids = list(map(int, self.get("abstract.id").keys()))
        potential_ids = set(range(1, len(existing_ids) + 2))
        return list(potential_ids - set(existing_ids))[0]

    def get_available_concrete_id(self):
        """Get the next available abstract id.

        Returns:
            int: The available id.
        """
        existing_ids = list(map(int, self.get("concrete.id").keys()))
        potential_ids = set(range(1, len(existing_ids) + 2))
        return list(potential_ids - set(existing_ids))[0]
