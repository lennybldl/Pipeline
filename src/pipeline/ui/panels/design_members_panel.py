"""Manage the design members panel."""

from pipeline.ui.panels import abstract_panel
from pipeline.ui.widgets import list_widget, tree_widget


class DesignMembersPanel(abstract_panel.AbstractPanel):
    """Manage the design members panel."""

    def build_ui(self, *args, **kwargs):
        """Build the widget's UI"""

        super(DesignMembersPanel, self).build_ui(*args, **kwargs)

        # save the lables font kwargs in a variable
        font_kwargs = {
            "bold": True,
            "font_size": 12,
            "alignment": "center",
        }

        # add a splitter
        splitter = self.layout.add_splitter("vertical")

        # add the concepts list
        widget = splitter.add_widget(margins=(0, 6, 0, 0))
        widget.layout.add_label("CONCEPT MEMBERS", **font_kwargs)
        self.concepts_list = list_widget.ConceptsListWidget()
        widget.layout.add_widget(self.concepts_list)

        # add the theoretical steps tree
        widget = splitter.add_widget(margins=(0, 6, 0, 0))
        widget.layout.add_label("THEORETICAL MEMBERS", **font_kwargs)
        self.theoretical_steps_tree = tree_widget.TheoreticalStepsTreeWidget()
        widget.layout.add_widget(self.theoretical_steps_tree)

        # set the splitter
        splitter.setSizes((100, 300))

    def sync(self, *args, **kwargs):
        """Synchronize the widget with the rest of the UI"""

        # inheritance
        super(DesignMembersPanel, self).sync(*args, **kwargs)

        self.concepts_list.sync()
        self.theoretical_steps_tree.sync()
