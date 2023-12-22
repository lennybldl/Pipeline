"""Manage the project of the pipeline."""

from python_core.types import dictionaries, signals

from pipeline.api import abstract_steps, concepts, concrete_steps
from pipeline.internal import core


class Project(dictionaries.Dictionary):
    """Manage elements of the project."""

    has_been_edited = False

    def __init__(self, *args, **kwargs):
        """Initialize the project."""

        # create signals
        self.changed = signals.Signal()

        # create a variable to list the edited members
        self.edited_members = dict()

        # initialize the object
        super(Project, self).__init__(*args, **kwargs)

        # connect signals
        self.changed.connect(self.project_changed_signal)

    def __repr__(self):
        """Override the __repr__ to visualize the member.

        Returns:
            str: The member's representation.
        """
        return "<(Project){}>".format(self.path)

    # global methods

    def load(self, *args, **kwargs):
        """Load the project."""
        super(Project, self).load(*args, **kwargs)
        # keep some global properties in memory
        self.properties_order = self.get("global.properies_order")

    def save(self):
        """Save the current project pipeline."""
        if self.has_been_edited:
            # save the project
            for path, member in self.edited_members.items():
                self.set(path, member.serialize())
            self.dump()
            # reset the project variables
            self.has_been_edited = False
            self.edited_members = dict()
            core.PROJECT_LOGGER.info("Save")
        else:
            core.PROJECT_LOGGER.info("No changes to save")

    # add members

    def add_member(self, member):
        """Add a member to the project and write it."""
        # save the member in its serialized form
        self.set(member.full_project_path, member.serialize())
        # connect the member changed signal to the project signal
        member.changed.connect(self.member_changed_signal, member)
        # emit a signal
        self.changed.emit()

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
        core.PROJECT_LOGGER.debug("Add concept. ID : '{}'".format(_id))

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
        core.PROJECT_LOGGER.debug("Add abstract step. ID : '{}'".format(_id))

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
        core.PROJECT_LOGGER.debug("Add concrete step. ID : '{}'".format(_id))

        return member

    # get members

    def get_member(self, path):
        """Get a member from the project.

        Arguments:
            path (str): A dot separated path to the member.

        Returns:
            Member: The desired member.
        """
        # get the member from the edited members
        if path in self.edited_members:
            return self.edited_members[path]

        # get the member from the project
        member = None
        if path:
            path, _, _id = path.rpartition(".")
            if "concept" in path:
                member = concepts.Concept(_id=_id)
            elif "abstract" in path:
                member = abstract_steps.AbstractStep(_id=_id)
            elif "concrete" in path:
                member = concrete_steps.ConcreteStep(_id=_id)

            # connect the member to the signals
            if member:
                member.changed.connect(self.member_changed_signal, member)

        return member

    def get_concept(self, _id):
        """Get a concept id.

        Arguments:
            _id (int): The id of the concept.

        Returns:
            Concept: The concept as a Concept.
        """
        return self.get_member("concept.id.{}".format(_id))

    def get_abstract_step(self, _id):
        """Get a abstract step id.

        Arguments:
            _id (int): The id of the abstract step.

        Returns:
            AbstractStep: The step as an AbstractStep.
        """
        return self.get_member("abstract.id.{}".format(_id))

    def get_concrete_step(self, _id):
        """Get a concrete step id.

        Arguments:
            _id (int): The id of the concrete step.

        Returns:
            ConcreteStep: The step as an ConcreteStep.
        """
        return self.get_member("concrete.id.{}".format(_id))

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

    # signals

    def project_changed_signal(self):
        """The mehod that is called when the project changed."""
        self.has_been_edited = True

    def member_changed_signal(self, member):
        """The mehod that is called when the project changed."""
        # sepcify that the project changed
        self.changed.emit()
        # add the member to the edited members
        if member not in self.edited_members:
            self.edited_members[member.full_project_path] = member
