"""Manage the tab where the design of the pipeline will be done."""

from pipeline.ui.tabs import abstract_tab
from pipeline.ui.panels import design_members_panel, design_members_properties_panel


class DesignTab(abstract_tab.AbstractTab):
    """Manage the design tab."""

    def build_ui(self, *args, **kwargs):
        """Build the widget's UI"""

        super(DesignTab, self).build_ui(*args, **kwargs)

        splitter = self.layout.add_splitter("horizontal", stretch=1)

        # The left side of the splitter
        members_panel = design_members_panel.DesignMembersPanel()
        splitter.add_widget(members_panel)

        # The right side of the splitter
        members_properties_panel = (
            design_members_properties_panel.DesignMembersPropertiesPanel()
        )
        splitter.add_widget(members_properties_panel)

        # edit the splitter
        splitter.setSizes((3, 1))

        # keep the panels in memory
        self.panels = [members_panel, members_properties_panel]

    def sync(self, *args, **kwargs):
        """Synchronize the widget with the rest of the UI"""

        super(DesignTab, self).sync(*args, **kwargs)

        for panel in self.panels:
            panel.sync()
