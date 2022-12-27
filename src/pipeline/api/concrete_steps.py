"""Manage the concrete steps."""

from pipeline.api import members


class ConcreteStep(members.Member):
    """Manage every concrete step of the pipeline."""

    project_path = "concrete.id"

    def create(self, abstract_step, **kwargs):
        """Create the member.

        Arguments:
            abstract_step (int, AbstractStep): The id or the abstract step this step
                inherits from.
        """
        super(ConcreteStep, self).create(**kwargs)
        self.add_property("int", "parent", kwargs.get("parent", 0))

        # set the super member of this member
        if isinstance(abstract_step, int):
            self.super_member = self.project.get("abstract.id.{}".format(abstract_step))
        else:
            self.super_member = abstract_step
