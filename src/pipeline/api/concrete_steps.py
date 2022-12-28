"""Manage the concrete steps."""

from pipeline.api import members


class ConcreteStep(members.Member):
    """Manage every concrete step of the pipeline."""

    project_path = "concrete.id"

    def _create_builtin_properties(self):
        """Create the builtin properties of the member.

        Builtin properties:
            | parent (int): The id of the step this step should be parented to.
                If 0, the step will be parented to the root. Default to 0.
        """
        super(ConcreteStep, self)._create_builtin_properties()
        self.add_property("int", "parent", 0)
