"""Manage the classes that control every member of the pipeline."""

from python_core.types import dictionaries, signals, strings

from pipeline.api import properties
from pipeline.internal import core


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

    def __repr__(self):
        """Override the __repr__ to visualize the member.

        Returns:
            str: The member's representation.
        """
        return "<{}>".format(self.full_project_path)

    # methods

    def create(self, super_member=None):
        """Create the member.

        Keyword Arguments:
            super_member (Member, optional): A member to inherit from. Default to None.
        """
        # add the super_member property to create an inheritance systems
        self.create_property("member", "super_member", visibility=core.PRIVATE)
        # add a sub_members property to list all the members that inherit from this one
        self.create_property("member_list", "sub_members", visibility=core.PRIVATE)

        # use the set property to call the callback
        self.set_property("super_member", super_member)

    def load(self):
        """Load the member from the project."""
        data = self.project.get(self.full_project_path)
        self.deserialize(data)

    def delete(self):
        """Delete the current member from the project."""
        self.project.pop(self.full_project_path)

    # serialization

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
            self.add_property_object(properties.load(name, value))

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
        self.add_property_object(_property)
        return _property

    def get_property(self, name):
        """Get the value of a property of this member.

        Arguments:
            name (str): The name of the property's value to get.

        Returns:
            Property, None: The desired property.
        """
        # get the value of any property of the member
        if "." in name and name != "super_member":
            property_name, attribute_name = name.split(".", 1)
            # get a value from the super member
            if property_name == "super_member":
                return self.super_member.get_property(attribute_name)
            # get a value from this member
            _property = self.get_property_object(property_name)
            return _property.query(attribute_name)

        # get a value from this member
        else:
            _property = self.get_property_object(name)
            return _property.query("value") if _property else None

    def set_property(self, name, value):
        """Set the value of a property of this member.

        Edit the property's value if its a property of the member or a public property
        of the super member

        Arguments:
            name (str): The name of the property.
            value (str): The value to set to the property.
        """
        # set an attribute on a property
        if "." in name:
            property_name, attribute_name = name.split(".", 1)
        # set the value of a property
        else:
            property_name = name
            attribute_name = "value"

        # set the property's attribute
        _property = self.get_property_object(property_name)
        if _property and (
            name in self.properties or _property.visibility == core.PUBLIC
        ):
            _property.edit(attribute_name, value)
            # refresh a property depending on its super member
            if self.is_initialized:
                self.refresh_property(name)
                for member in self.sub_members:
                    member.refresh_property(name)

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
            self.changed.emit()

    def refresh_property(self, name):
        """Refresh the member's property depending on the super member.

        Arguments:
            name (str): the name of the property to refresh.
        """
        # do not refresh if not super member or if it is a the sticky property
        super_member = self.super_member
        if not super_member or name in core.STICKY_PROPERTIES:
            return

        # do not clean if no super property
        super_property = super_member.get_property_object(name)
        if not super_property:
            return

        if name in self.properties:
            # remove the name property if the super member has a procedural name
            if name == "name" and super_member.has_procedural_name():
                self.delete_property("name")
                return

            # get the property to compare to the super property
            _property = self.get_property_object(name)

            # compare the properties to define if they need to be changed
            if super_property.visibility == core.PUBLIC:
                # remove the property of the member if the properties are identical
                if _property == super_property:
                    self.delete_property(name)
            # remove the property if the super property is protected
            elif super_property.visibility == core.PROTECTED:
                self.delete_property(name)
            # add the property to the member if the super property is private
            elif super_property.visibility == core.PRIVATE:
                self.add_property_object(super_property.copy())

    # properties objects methods

    def add_property_object(self, _property):
        """Add a property object to this member.

        Arguments:
            _property (Property): The property to add.
        """
        if not _property.member == self:
            # add the property to the member's properties
            name = _property.name
            self.properties[name] = _property
            _property.member = self

            # connect the property's signal to this member
            _property.changed.connect(self.changed.emit)

            # emit a signal to stipulate that the member has been edited
            if self.is_initialized:
                self.changed.emit()

    def get_property_object(self, name, recursive=True):
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
        super_member = self.super_member
        if recursive and super_member:
            _property = super_member.get_property_object(name)
            if _property and _property.visibility != core.PRIVATE:
                # copy the property and link it to the member
                _property = _property.copy()
                _property.changed.connect(self.add_property_object, _property)
                return _property

        # return nothing if no property found
        return

    def get_properties_objects(self):
        """Get all the properties objects available on this member.

        Returns:
            dict: A dictionary of properties.
        """
        properties = dict()
        if self.super_member:
            properties.update(self.super_member.get_properties_objects())
        properties.update(self.properties)
        return properties

    # private methods

    def create_builtin_properties(self):
        """Create the builtin properties of the member.

        This method can be extended to add builtin properties.
        """
        self.create_property("str", "name", self.__class__.__name__ + str(self._id))
        self.create_property("str", "alias", "")
        self.create_property("int", "index", "index")
        self.create_property("int", "padding", 0)
        self.create_property("commands", "commands", dict())

    # custom methods

    def has_procedural_name(self):
        """Get if the member has a procedural name or a fixed one.

        Returns:
            bool: true if the name is procedural, else False.
        """
        return "{" in self.get_property("name")

    def get_formated_name(self):
        """Get the formated name of the member.

        Returns:
            str: The formated name of the member.
        """
        name = self.get_property("name")

        if self.has_procedural_name():
            # get the properties written in the procedural name
            properties = dict()
            for _property in strings.isolate_inbetween(name, "{", "}"):
                properties["{%s}" % _property] = self.get_property(_property)

            # replace the properties in the name by their values
            return strings.replace(name, properties.keys(), properties.values())

        return name

    def call(self, name):
        """Call a command on this member.

        Arguments:
            name (str): The name of the command to call.
        """
        software = core.MANAGER.software
        command = self.commands.get("{}.{}".format(software, name))
        if command is None:
            core.LOGGER.error(
                "No command '{}' found for '{}' on {}.".format(
                    name, software, self.full_project_path
                )
            )
        else:
            command.call(self)

    # callbacks

    def super_member_set_value_pre_callback(self, super_member):
        """Create a callback for the super member property.

        This callback will be called before setting the property.

        Arguments:
            super_member (Member): The new super member.
        """
        # remove this member for the current super member sub_members property
        if self.super_member:
            sub_members = self.super_member.get_property_object("sub_members")
            sub_members.remove(self)

    def super_member_set_value_post_callback(self, super_member):
        """Create a callback for the super member property.

        This callback will be called after setting the property.

        Arguments:
            super_member (Member): The new super member.
        """
        # merge the builtin properties of the member
        if super_member:
            # remove the properties if they're identical to the super member's
            properties = self.properties.copy()
            for name in properties.keys():
                if name not in core.STICKY_PROPERTIES:
                    self.refresh_property(name)

            # append this member to the new super member sub_members property
            sub_members = super_member.get_property_object("sub_members")
            sub_members.append(self)

        # create the builtin properties of the member if no super member
        else:
            self.create_builtin_properties()

    # properties

    def get_super_member(self):
        """Get the super member of the member.

        Returns:
            Member: The super member.
        """
        return self.get_property("super_member")

    def set_super_member(self, super_member):
        """Set the super member of the member.

        Arguments:
            super_member (Member): The super member.
        """
        self.set_property("super_member", super_member)

    super_member = property(get_super_member, set_super_member)

    def get_sub_members(self):
        """Get the sub members of the member.

        Returns:
            list: The sub members.
        """
        return self.get_property("sub_members")

    def set_sub_members(self, sub_members):
        """Set the sub members of the member.

        Arguments:
            sub_members (list): The sub members.
        """
        self.set_property("sub_members", sub_members)

    sub_members = property(get_sub_members, set_sub_members)

    @property
    def project(self):
        """Get the current project.

        Returns:
            Project: The current project.
        """
        return core.MANAGER.project

    @property
    def full_project_path(self):
        """Get the full project path of the current member.

        Returns:
            str: The member's full project path.
        """
        return "{}.{}".format(self.project_path, self._id)


class DesignMember(Member):
    """Manage a design member of the pipeline."""
