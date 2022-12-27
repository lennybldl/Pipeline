"""Manage the abstract steps."""

from pipeline.api import members


class AbstractStep(members.DesignMember):
    """Manage every abstract step of the pipeline."""

    project_path = "abstract.id"

    def create(self, **kwargs):
        """Create the member.

        Keyword Arguments:
            parent (int, optional): The id of the step this step should be parented to.
                If 0, the step will be parented to the root. Default to 0.
        """
        super(AbstractStep, self).create(**kwargs)
        self.add_property("int", "parent", kwargs.get("parent", 0))
