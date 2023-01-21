"""Manage the classes that control every member of the pipeline."""

from python_core.types import dictionaries, signals, strings

from pipeline.api import properties
from pipeline.internal import manager


class Member(object):
    """Manage every member of the pipeline."""

    properties = dict()  # properties (dict): Store the properties of the member
    project_path = ""  # project_path (str): The path to store the member in the project

    is_initialized = False

    def __init__(self, _id, super_member=None):
        """Initialize the member.

        Keyword Arguments:
            super_member (Member, optional): A member to inherit from. Default to None.
        """
        # create signals
        self.changed = signals.Signal()

        # initialize the object
        super(Member, self).__init__()

        self._id = _id
        self.properties = dict()

        # initialize the member either from data or create it with custom properties
        if str(_id) in self.project.get(self.project_path):
            self.load()
        else:
            self.create(super_member)

        # set the property initialized
        self.is_initialized = True

    # methods

    def create(self, super_member=None):
        """Create the member.

        Keyword Arguments:
            super_member (Member, optional): A member to inherit from. Default to None.

        """
        # add the super member property to create inheritance systems
        self.create_property("member", "super_member", super_member)
        self.super_member_callback()

    def load(self):
        """Load the member from the project.

        Returns:
            dict: The member's properties from the project.
        """
        data = self.project.get(self.full_project_path)
        self.deserialize(data)

    def serialize(self):
        """Serialize the member's properties to write them in the project.

        Returns:
            Dictionary: The dictionary ready for serialization.
        """

        serialization = dictionaries.Dictionary()

        # get the serialization order
        order = self.project.properties_order
        custom_keys = list(set(sorted(self.properties.keys())) - set(order))
        order.extend(custom_keys)

        # serialize the properties
        serialization["properties"] = _properties = dictionaries.Dictionary()
        for key in order:
            if key in self.properties:
                _property = self.properties.get(key)
                _properties[key] = _property.serialize()

        return serialization

    def deserialize(self, data):
        """Deserialize data to set the member properties.

        Arguments:
            data (dict): A serialized version of the member.
        """
        # deserialize the properties
        self.properties = dict()
        for name, value in data["properties"].items():
            self.add_property(properties.load(name, value))

    def delete(self):
        """Delete the current member from the project."""
        self.project.pop(self.full_project_path)

    # properties methods

    def create_property(self, data_type, name, *args, **kwargs):
        """Create and add a new property to this member.

        Arguments:
            data_type (str): The property's data type.
            name (str): The name of the property.

        Returns:
            Property: The created property.
        """
        _property = properties.create(data_type, name, *args, **kwargs)
        self.add_property(_property)
        return _property

    def add_property(self, _property):
        """Add a property object to this member.

        Arguments:
            _property (Property): The porperty to add.
        """
        # add the property to the member's properties
        name = _property.name
        self.properties[name] = _property

        # connect the property's signal to this member
        _property.changed.connect(self.changed.emit)
        _property.changed.connect(lambda: self._update_property(_property))

        # connect the property to its callback
        callback = "{}_callback".format(name)
        if hasattr(self, callback):
            _property.changed.connect(getattr(self, callback))

        # update the project with the new property
        self._update_property(_property)
        # emit a signal to stipulate that the member has been edited
        if self.is_initialized:
            self.changed.emit()

    def get_property(self, name, recursive=True):
        """Get a property of this member.

        Arguments:
            name (str): The name of the property to get.

        Keyword Arguments:
            recursive (bool, optional): To get the property from the super member too.
                Default to True.

        Returns:
            Property, None: The desired property.
        """
        # get the property from the current member
        if name in self.properties:
            return self.properties[name]

        # get the property from the super member
        if recursive and self.super_member:
            _property = self.super_member.get_property(name)
            if _property:
                # copy the property and link it to the member
                _property = _property.copy()
                _property.changed.connect(lambda: self._update_property(_property))
                return _property

        # return nothing if no property found
        return

    def delete_property(self, name):
        """Delete a property from the member.

        Arguments:
            name (str): The name of the property.
        """
        if name in self.properties:
            self.properties.pop(name)
            self.project.pop(
                "{}.{}.properties.{}".format(self.project_path, self._id, name)
            )

    def get_properties(self):
        """Get all the properties available on this member.

        Returns:
            dict: A dictionary of properties.
        """
        properties = dict()
        if self.super_member:
            properties.update(self.super_member.get_properties())
        properties.update(self.properties)
        return properties

    # properties values methods

    def get_value(self, name):
        """Get the value of a property of this member.

        Arguments:
            name (str): The name of the property's value to get.

        Returns:
            Property, None: The desired property.
        """
        # get the super member
        if name == "super_member":
            _property = self.get_property("super_member")
            return _property.value if _property else _property

        # get the value of any property of the member
        elif "." in name:
            property_name, attribute_name = name.split(".", 1)
            # get a value from the super member
            if property_name == "super_member":
                return self.super_member.get_value(attribute_name)
            # get a value from this member
            _property = self.get_property(property_name)
            return _property.get_attribute(attribute_name)

        # get a value from this member
        else:
            _property = self.get_property(name)
            return _property.value if _property else _property

    def set_value(self, name, value):
        """Set the value of a property of this member.

        Edit the property's value if its a property of the member or a public property
        of the super member

        Arguments:
            name (str): The name of the property's value to set.
            value (-): The value to set.
        """
        # set an attribute on a property
        if "." in name:
            property_name, attribute_name = name.split(".", 1)
            _property = self.get_property(property_name)
            if _property and (
                name in self.properties or _property.visibility == "public"
            ):
                _property.set_attribute(".".join(attribute_name), value)

        else:
            _property = self.get_property(name)
            if _property and (
                name in self.properties or _property.visibility == "public"
            ):
                _property.value = value

    # private methods

    def _update_property(self, _property):
        """Update a property in the project.

        Arguments:
            _property (Property): The porperty to update in the project.
        """
        # add the property to the member if it isn't already in the member's properties
        if _property.name not in self.properties:
            self.add_property(_property)

        # update the value of the property
        else:
            self.project.set(
                "{}.properties.{}".format(self.full_project_path, _property.name),
                _property.serialize(),
            )

    def _create_builtin_properties(self, **kwargs):
        """Create the builtin properties of the member.

        Builtin properties:
            | name (str): The name to give to the member. It can be hard
                    coded or made up of variables within braces.
                    (e.g : "TheName", "Abstract_{concept}"). Default to "ClassName#".
            | alias (int): The name to give to the member that overrides
                the name. Default to None.
            | index (int): The id of the member. Default to 0.
            | padding (int): The number of digits in the index. Default to 4.
            | commands (dict): The member's commands. Default to dict().
        """
        default_name = self.__class__.__name__ + str(self._id)
        self.create_property("str", "name", kwargs.get("name", default_name))
        self.create_property("str", "alias", kwargs.get("alias", ""))
        self.create_property("int", "index", kwargs.get("index", 0))
        self.create_property("int", "padding", kwargs.get("padding", 0))
        self.create_property("commands", "commands", kwargs.get("commands", dict()))

    def _clean_properties(self):
        """Clean the properties to make the project lighter."""
        # clean the properties if there the save as the super member
        super_member = self.super_member
        if super_member:
            properties = self.properties.copy()
            for name, _property in properties.items():
                super_member_property = super_member.get_property(name)
                if super_member_property and _property == super_member_property:
                    self.delete_property(name)

    # custom methods

    def has_procedural_name(self):
        """Get if the member has a procedural name or a fixed one.

        Returns:
            bool: true if the name is procedural, else False.
        """
        return "{" in self.get_value("name")

    def get_formated_name(self):
        """Get the formated name of the member.

        Returns:
            str: The formated name of the member.
        """
        name = self.get_value("name")

        if self.has_procedural_name():
            # get the properties written in the procedural name
            properties = dict()
            for _property in strings.isolate_inbetween(name, "{", "}"):
                properties["{%s}" % _property] = self.get_value(_property)

            # replace the properties in the name by their values
            return strings.replace(name, properties.keys(), properties.values())

        return name

    def call(self, name):
        """Call a command on this member.

        Arguments:
            name (str): The name of the command to call.
        """
        software = manager.get_software()
        command = self.commands.get("{}.{}".format(software, name))
        if command is None:
            manager.LOGGER.error(
                "No command '{}' found for '{}' on {}.".format(
                    name, software, self.full_project_path
                )
            )
        else:
            command.call(self)

    # callback

    def super_member_callback(self):
        """Create a callback for the super member property."""
        super_member = self.super_member

        # merge the builtin properties of the member
        if super_member:
            self._clean_properties()
            # remove the property's name if the super member has procedural names
            if super_member.has_procedural_name():
                self.delete_property("name")

        # create the builtin properties of the member
        else:
            self._create_builtin_properties()

    # properties

    def get_super_member(self):
        """Get the super member of the member.

        Returns:
            Member: The super member.
        """
        return self.get_value("super_member")

    def set_super_member(self, super_member):
        """Set the super member of the member.

        Arguments:
            super_member (Member): The super member.
        """
        return self.set_value("super_member", super_member)

    super_member = property(get_super_member, set_super_member)

    @property
    def project(self):
        """Get the current project.

        Returns:
            Project: The current project.
        """
        return manager.get_project()

    @property
    def full_project_path(self):
        """Get the full project path of the current member.

        Returns:
            str: The member's full project path.
        """
        return "{}.{}".format(self.project_path, self._id)


class DesignMember(Member):
    """Manage a design member of the pipeline."""
