"""Manage the editing of the design members."""

from pipeline.ui.panels import abstract_panel

from pipeline.internal import database

DATABASE = database.Database()

# UI variables
LABELS_WIDTH = 80


class DesignMembersPropertiesPanel(abstract_panel.AbstractPanel):
    """Manage the design members properties panel."""

    _margins = (0, 9, 0, 0)

    properties = dict()

    def build_ui(self, *args, **kwargs):
        """Build the widget's UI"""

        super(DesignMembersPropertiesPanel, self).build_ui(*args, **kwargs)

        # set up variables to lighten the code
        font_kwargs = {"bold": True}

        self.layout.add_label("PROPERTIES", font_size=12, bold=True, alignment="center")

        # global properties
        self.layout.add_label("Global properties", **font_kwargs)
        global_widget = self.layout.add_group_box(margins=5)
        layout = global_widget.layout.add_layout("horizontal")
        layout.add_label("Index padding", setFixedWidth=LABELS_WIDTH)
        layout.add_spin_box(value=4)

        # private properties
        self.layout.add_label("Private properties", **font_kwargs)
        self.private_widget = self.layout.add_group_box(margins=5, spacing=2)
        # id
        layout = self.private_widget.layout.add_layout(orientation="horizontal")
        layout.add_label("id", setFixedWidth=LABELS_WIDTH)
        self.id_field = layout.add_spin_box()
        self.id_field.setEnabled(False)
        # procedural fields
        self._add_procedural_fields()
        self.private_widget.setEnabled(False)

        # custom properties
        self.layout.add_label("Custom properties", **font_kwargs)
        self.layout.add_group_box()

    def _add_procedural_fields(self):
        """Add the procedural fields to the UI."""

        # type
        layout = self.private_widget.layout.add_layout(orientation="horizontal")
        label = layout.add_label("type", setFixedWidth=LABELS_WIDTH)
        widget = layout.add_combo_box(["asset", "task", "workfile"])
        self.properties["type"] = {
            "widgets": (label, widget),
            "command": widget.setCurrentText,
        }

        # name
        layout = self.private_widget.layout.add_layout(orientation="horizontal")
        label = layout.add_label("name", setFixedWidth=LABELS_WIDTH)
        widget = layout.add_line_edit(setPlaceholderText="name")
        self.properties["name"] = {
            "widgets": (label, widget),
            "command": widget.setText,
        }

        # task
        layout = self.private_widget.layout.add_layout(orientation="horizontal")
        label = layout.add_label("task", setFixedWidth=LABELS_WIDTH)
        widget = layout.add_line_edit(setPlaceholderText="task")
        self.properties["task"] = {
            "widgets": (label, widget),
            "command": widget.setText,
        }

        # index padding
        layout = self.private_widget.layout.add_layout(orientation="horizontal")
        label = layout.add_label("index padding", setFixedWidth=LABELS_WIDTH)
        widget = layout.add_spin_box()
        self.properties["index_padding"] = {
            "widgets": (label, widget),
            "command": widget.setValue,
        }

        # concept
        layout = self.private_widget.layout.add_layout(orientation="horizontal")
        label = layout.add_label("concept", setFixedWidth=LABELS_WIDTH)
        self.concept_field = layout.add_combo_box(["asset", "task", "workfile"])
        self.properties["concept"] = {
            "widgets": (label, self.concept_field),
            "command": self.concept_field.setCurrentIndex,
        }

        # rules
        self.private_widget.layout.add_list_widget(stretch=1)

    # methods

    def sync(self, _id=None, *args, **kwargs):
        """Synchonize the widget with the rest of the UI.

        Keyword Arguments:
            _id (Member, optional): The member to edit the properties from.
                Default to None.
        """

        super(DesignMembersPropertiesPanel, self).sync(*args, **kwargs)

        # disable the widget if no _id specifyied
        if _id is None:
            self.private_widget.setEnabled(False)
            return

        self.private_widget.setEnabled(True)

        # update the id of the current member
        self.id_field.setValue(_id)

        # update the concepts choices
        concepts = DATABASE.config.get("concepts.id")
        self.concept_field.clear()
        self.concept_field.add_items(
            [concepts.get("{}.name".format(i)) for i in range(len(concepts))]
        )

        # update the properties with the current id
        id_properties = _id.get_properties()
        for _property, values in self.properties.items():

            if _property in id_properties:
                # display the property and set it
                for widget in values["widgets"]:
                    widget.setVisible(True)
                    widget.setEnabled(True)
                values["command"](id_properties[_property])

            else:
                # hide the property
                for widget in values["widgets"]:
                    widget.setVisible(False)
                    widget.setEnabled(False)
