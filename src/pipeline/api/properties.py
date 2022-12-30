"""Manage the properties for each member."""

from python_core.types import dictionaries, signals

from pipeline.internal import manager

VISIBILITY_MODES = ["public", "protected", "private"]


class Property(object):
    """Create a property class to store informations."""

    data_type = None
    default_value = None
    visibility = "public"
    display = True

    is_initialized = False

    def __init__(self, name, *args, **kwargs):
        """Initialize the property.

        Arguments:
            name (str): The name of the property.

        Keyword Arguments:
            value (-, optional): The value to give to the property.
                Default to self.default_value.
            visibility (str, optional): The visibility of the property.
                | "public" : readable and writable by sub members
                | "protected" : readable and but not writable by sub members
                | "private" : neither readable nor writable by sub members
                Default to "public".
            display (bool, optional): Wether or not the the property is displayable
                in the UI. Default to True.
        """
        # create signals
        self.has_been_edited = signals.Signal()

        # initialize the object
        super(Property, self).__init__()

        # create the property
        self.name = name
        self.create(*args, **kwargs)

        # set the property initialized
        self.is_initialized = True

    def __repr__(self):
        """Override the __repr__ to visualize the property.

        Returns:
            str: the property representation.
        """
        return "({}){}:{}".format(self.visibility.title(), self.name, self.value)

    def __set__(self, instance, value):
        """Override the __set__ method to edit the value of the property.

        Arguments:
            instance (instance): Instance is the instance that the attribute was
                accessed through, or None when the attribute is accessed
                through the owner.
            value (-): The value to set.
        """
        self.value = value

    def __setattr__(self, name, value):
        """Override the __setattr__ to emit a signal when the property is edited."""

        super(Property, self).__setattr__(name, value)

        # emit a signal to stipulate that the property has been edited
        if self.is_initialized:
            self.has_been_edited.emit()

    def __eq__(self, other):
        """Compare two properties together.

        Arguments:
            other (object): The property object or the value to compare with.

        Returns:
            bool: True if they're equal, else False.
        """
        if isinstance(other, Property):
            return self.serialize() == other.serialize()
        return self.value == other

    def __ne__(self, other):
        """Compare two properties together.

        Arguments:
            other (object): The property object or the value to compare with.

        Returns:
            bool: True if they are not equal, else False.
        """
        if isinstance(other, Property):
            return self.serialize() != other.serialize()
        return self.value != other

    # methods

    def create(self, *args, **kwargs):
        """Create the property."""
        self.value = kwargs.get("value", args[0] if args else self.default_value)
        self.visibility = kwargs.pop("visibility", self.visibility)
        self.display = kwargs.pop("display", self.display)

    def load(self, data):
        """Load the property from a serialized dictionary.

        Arguments:
            data (dict): The data to recreate the property from.
        """
        # deserialize the settings
        setup = data.pop("setup")
        setup = setup.split("-")[1]
        self.visibility = VISIBILITY_MODES[int(setup[0])]
        self.display = bool(setup[1])

        # deserialize all the data
        for key, value in data.items():
            setattr(self, key, value)

    def serialize(self):
        """Serialize the property to write it in the project.

        Returns:
            Dictionary: The dictionary ready for serialization.
        """
        serialization = dictionaries.Dictionary()

        # write the serialization
        serialization["setup"] = "{}-{}{}".format(
            self.data_type, VISIBILITY_MODES.index(self.visibility), int(self.display)
        )
        serialization["value"] = self._get_serialized_value()

        return serialization

    # private methods

    def _get_serialized_value(self):
        """Get the value in a serialized form.

        Returns:
            -: The serialized value.
        """
        return self.value


class BoolProperty(Property):
    """Store a bool information."""

    data_type = "bool"
    default_value = ""


class NumericProperty(Property):
    """Store a numeric information."""

    min = None
    max = None
    default_value = 0

    # methods

    def create(self, *args, **kwargs):
        """Create the property."""
        self.min = kwargs.pop("min", None)
        self.max = kwargs.pop("max", None)
        super(NumericProperty, self).create(*args, **kwargs)

    def serialize(self):
        """Serialize the property to write it in the project.

        Returns:
            Dictionary: The dictionary ready for serialization.
        """
        serialization = super(NumericProperty, self).serialize()

        # set the min and max value
        if self.min is not None:
            serialization["min"] = self.min
        if self.max is not None:
            serialization["max"] = self.max

        return serialization


class IntProperty(NumericProperty):
    """Store an integer information."""

    data_type = "int"


class FloatProperty(NumericProperty):
    """Store a float information."""

    data_type = "float"


class StrProperty(Property):
    """Store a string information."""

    data_type = "str"
    default_value = ""


class ListProperty(Property):
    """Store a list information."""

    data_type = "list"
    default_value = list()


class DictProperty(Property):
    """Store a dictionary information."""

    data_type = "dict"
    default_value = dict()


class EnumProperty(Property):
    """Store an enum information."""

    data_type = "enum"
    default_value = list()


class MemberProperty(Property):
    """Store a member information."""

    data_type = "member"

    # methods

    def load(self, data):
        """Load the property from a serialized dictionary.

        Arguments:
            data (dict): The data to recreate the property from.
        """
        project = manager.get_project()
        value = data.pop("value")
        self.value = project.get_member(value) if value else value
        super(MemberProperty, self).load(data)

    def _get_serialized_value(self):
        """Get the value in a serialized form.

        Returns:
            str: The serialized value.
        """
        # save the member path
        if self.value:
            return "{}.{}".format(self.value.project_path, self.value._id)


class CompoundProperty(Property):
    """Store multiple properties information."""

    data_type = "compound"

    def __getitem__(self, name):
        """Get an attribute from the property.

        Arguments:
            name (str): The name of the attribute or property.

        Returns:
            -: The attribute.
        """
        return self.value.get(name)

    # methods

    def create(self, *args, **kwargs):
        """Create the property."""
        super(CompoundProperty, self).create(*args, **kwargs)
        self.value = dict()

    def load(self, data):
        """Load the property from a serialized dictionary.

        Arguments:
            data (dict): The data to recreate the property from.
        """
        # deserialize the value
        self.value = dict()
        for name, properties_data in data.pop("value").items():
            self.value[name] = load(name, properties_data)

        # deserialize the rest of the property
        super(CompoundProperty, self).load(data)

    def add_property(self, data_type, name, *args, **kwargs):
        """Create and add a new property to this member.

        Arguments:
            data_type (str): The property's data type.
            name (str): The name of the property.

        Returns:
            Property: The created property.
        """
        _property = create(data_type, name, *args, **kwargs)
        self.value[name] = _property

        # connect the property's signal to this property
        _property.has_been_edited.connect(self.has_been_edited.emit)

        # emit a signal to stipulate that the property has been changed
        self.has_been_edited.emit()

        return _property

    # private methods

    def _get_serialized_value(self):
        """Get the value in a serialized form.

        Returns:
            -: The serialized value.
        """
        serialization = dictionaries.Dictionary()

        for name, _property in self.value.items():
            serialization[name] = _property.serialize()

        return serialization


INDEXES_TYPES = {
    "bool": BoolProperty,
    "int": IntProperty,
    "float": FloatProperty,
    "str": StrProperty,
    "list": ListProperty,
    "dict": DictProperty,
    "enum": EnumProperty,
    "member": MemberProperty,
    "compound": CompoundProperty,
}


def create(data_type, name, *args, **kwargs):
    """Create a property.

    Arguments:
        data_type (str): The property's data type.
        name (str): The name of the property.
    """
    _property = INDEXES_TYPES[data_type]
    _property = _property(name, *args, **kwargs)
    return _property


def load(name, data):
    """Get a property from its serialized data.

    Arguments:
        name (str): The name to giveto the property.
        data (dict): The serialized data of the property.

    Returns:
        Property: The deserialized property instance.
    """
    data_type = data["setup"].split("-")[0]
    _property = INDEXES_TYPES[data_type]
    _property = _property(name)
    _property.load(data.copy())
    return _property
