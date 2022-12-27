"""Manage the tab where we manage the actual project."""

from pipeline.ui.tabs import abstract_tab
from pipeline.ui.panels import concrete_members_panel


class ProjectTab(abstract_tab.AbstractTab):
    """Manage the project tab."""

    def build_ui(self, *args, **kwargs):
        """Build the widget's UI"""

        super(ProjectTab, self).build_ui(*args, **kwargs)

        # add the concrete steps tree panel
        members_panel = concrete_members_panel.ConcreteMembersPanel()
        self.layout.add_widget(members_panel)

        # keep the panels in memory
        self.panels = [members_panel]

    def sync(self, *args, **kwargs):
        """Synchronize the widget with the rest of the UI"""

        super(ProjectTab, self).sync(*args, **kwargs)

        for panel in self.panels:
            panel.sync()
