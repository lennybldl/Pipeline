"""Manage the abstract steps."""

from pipeline.api import members


class AbstractStep(members.DesignMember):
    """Manage every abstract step of the pipeline."""

    project_path = "abstract.id"

    def _create_builtin_properties(self):
        """Create the builtin properties of the member.

        Builtin properties:
            | parent (int): The id of the step this step should be parented to.
                If 0, the step will be parented to the root. Default to 0.
        """
        super(AbstractStep, self)._create_builtin_properties()
        self.add_property("int", "parent", 0)
