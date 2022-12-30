"""Manage the classes that control every member of the pipeline."""

from python_core.types import dictionaries, signals, strings

from pipeline.api import properties
from pipeline.internal import manager


class Member(object):
    """Manage every member of the pipeline."""

    super_member = None  # super_member (Member): The parent to inherit from
    properties = dict()  # properties (dict): Store the properties of the member
    project_path = ""  # project_path (str): The path to store the member in the project

    is_initialized = False

    def __init__(self, _id, super_member=None):
        """Initialize the member.

        Keyword Arguments:
            super_member (Member, optional): A member to inherit from. Default to None.
        """
        # create signals
        self.has_been_edited = signals.Signal()

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

    def __setattr__(self, name, value):
        """Override the __setattr__ to set the properties values.

        Arguments:
            name (str): The name of the attribute to set.
            value (value): The value to give to the attribute.
        """
        # edit the properties if possible, else edit a normal attribute
        if not self.set_property(name, value):
            super(Member, self).__setattr__(name, value)

    def __getattribute__(self, name):
        """Get an attribute from the member or its super member.

        Arguments:
            name (str): The name of the attribute or property.

        Returns:
            -: The attribute.
        """
        try:
            attribute = object.__getattribute__(self, name)
            if isinstance(attribute, properties.Property):
                return attribute.value
            return attribute
        except AttributeError:
            if self.super_member:
                return getattr(self.super_member, name)

        raise AttributeError("'{}' has no attribute '{}'".format(self.__class__, name))

    # methods

    def create(self, super_member=None):
        """Create the member.

        Keyword Arguments:
            super_member (Member, optional): A member to inherit from. Default to None.

        """
        # add the super member property to create inheritance systems
        self.add_property("member", "super_member", super_member)
        self.super_member_callback()

    def load(self):
        """Load the member from the project.

        Returns:
            dict: The member's properties from the project.
        """
        data = self.project.get("{}.{}".format(self.project_path, self._id))
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

        # serialize the porperties
        for key in order:
            if key in self.properties:
                _property = self.properties.get(key)
                serialization[key] = _property.serialize()

        return serialization

    def deserialize(self, data):
        """Deserialize data to set the member properties.

        Arguments:
            data (dict): A serialized version of the member.
        """
        self.properties = dict()
        for name, value in data.items():
            self._add_property(name, properties.load(name, value))

    def delete(self):
        """Delete the current member from the project."""
        self.project.pop("{}.{}".format(self.project_path, self._id))

    # properties methods

    def add_property(self, data_type, name, *args, **kwargs):
        """Create and add a new property to this member.

        Arguments:
            data_type (str): The property's data type.
            name (str): The name of the property.

        Returns:
            Property: The created property.
        """
        _property = properties.create(data_type, name, *args, **kwargs)
        self._add_property(name, _property)

        # update the project with the new property
        self._update_property(name)

        # emit a signal to stipulate that the member has been edited
        if self.is_initialized:
            self.has_been_edited.emit()

        return _property

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
        _properties = self.get_properties() if recursive else self.properties
        return _properties.get(name)

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

    def set_property(self, name, value):
        """Set the value of a property.

        Arguments:
            name (str): The name of the property.
            value (-): The value to set to the property.

        Returns:
            bool: True if the value was set, else False.
        """
        # edit the properties
        _property = self.get_property(name)
        if _property:
            # edit the property's value if it exists
            if _property.name in self.properties:
                _property.value = value
                return True
            # override the property if it is public
            elif _property.visibility == "public":
                self.add_property(_property.data_type, name, value)
                return True

        return False

    def delete_property(self, name):
        """Delete a property from the member.

        Arguments:
            name (str): The name of the property.
        """
        if name in self.properties:
            self.properties.pop(name)
            delattr(self, name)
            self._update_property(name)

    # private methods

    def _add_property(self, name, _property):
        """Add a property object to this member.

        Arguments:
            name (str): The name of the property.
            _property (Property): The porperty to associate to the name.
        """
        # add the property to the member's properties
        super(Member, self).__setattr__(name, _property)
        self.properties[name] = _property

        # connect the property's signal to this member
        _property.has_been_edited.connect(self.has_been_edited.emit)
        _property.has_been_edited.connect(lambda: self._update_property(name))

        # connect the property to its callback
        callback = "{}_callback".format(name)
        if hasattr(self, callback):
            _property.has_been_edited.connect(getattr(self, callback))

    def _update_property(self, name):
        """Update a property in the project.

        Arguments:
            name (str): The name of the property to udpate.
        """
        # update the value of the property
        if name in self.properties:
            _property = self.properties[name]
            self.project.set(
                "{}.{}.{}".format(self.project_path, self._id, name),
                _property.serialize(),
            )
        # remove the property
        else:
            self.project.pop("{}.{}.{}".format(self.project_path, self._id, name))

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
            | rules (dict): The member's rules. Default to 4.
        """
        default_name = self.__class__.__name__ + str(self._id)
        self.add_property("str", "name", kwargs.get("name", default_name))
        self.add_property("str", "alias", kwargs.get("alias", ""))
        self.add_property("int", "index", kwargs.get("index", 0))
        self.add_property("int", "padding", kwargs.get("padding", 0))
        self.add_property("dict", "rules", kwargs.get("rules", dict()))

    # custom methods

    def has_procedural_name(self):
        """Get if the member has a procedural name or a fixed one.

        Returns:
            bool: true if the name is procedural, else False.
        """
        return "{" in self.name

    def get_name(self):
        """Get the name property's value.

        If the name is a procedural name, it will return the formated name

        Returns:
            str: The formated name of the member.
        """
        name = self.name

        if self.has_procedural_name():
            # get the properties written in the procedural name
            properties = dict()
            for _property in strings.isolate_inbetween(name, "{", "}"):
                # get recursive properties
                if "." in _property:
                    result = self
                    for prop in _property.split("."):
                        result = getattr(result, prop)
                    properties["{%s}" % _property] = result
                # get properties from this member
                else:
                    properties["{%s}" % _property] = getattr(self, _property)

            # replace the properties in the name by their values
            return strings.replace(name, properties.keys(), properties.values())

        return name

    # callback

    def super_member_callback(self):
        """Create a callback for the super member property."""
        super_member = self.super_member

        # merge the builtin properties of the member
        if super_member:
            properties = self.properties.copy()
            for name, _property in properties.items():
                super_member_property = super_member.get_property(name)
                if super_member_property and _property == super_member_property:
                    self.delete_property(name)
            # remove the property's name if the super member has procedural names
            if super_member.has_procedural_name():
                self.delete_property("name")

        # create the builtin properties of the member
        else:
            self._create_builtin_properties()

    # properties

    @property
    def project(self):
        """Get the current project.

        Returns:
            Project: The current project.
        """
        return manager.get_project()


class DesignMember(Member):
    """Manage a design member of the pipeline."""
