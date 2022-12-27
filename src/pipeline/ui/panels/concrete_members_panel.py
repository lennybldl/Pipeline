"""Manage the concrete members panel."""

from pipeline.ui.panels import abstract_panel
from pipeline.ui.widgets import tree_widget


class ConcreteMembersPanel(abstract_panel.AbstractPanel):
    """Manage the concrete members panel."""

    def build_ui(self, *args, **kwargs):
        """Build the widget's UI"""

        super(ConcreteMembersPanel, self).build_ui(*args, **kwargs)

        # add the concrete steps tree
        self.layout.add_label(
            "CONCRETE MEMBERS",
            name="header_1",
            bold=True,
            font_size=12,
            alignment="center",
        )
        self.concrete_steps_tree = tree_widget.ConcreteStepsTreeWidget()
        self.layout.add_widget(self.concrete_steps_tree)

    def sync(self, *args, **kwargs):
        """Synchronize the widget with the rest of the UI"""

        # inheritance
        super(ConcreteMembersPanel, self).sync(*args, **kwargs)

        self.concrete_steps_tree.sync()
