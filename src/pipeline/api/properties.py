"""Manage the properties for each member."""

from python_core.types import dictionaries, signals

from pipeline.api import commands
from pipeline.internal import manager, properties_values

MANAGER = manager.Manager()
VISIBILITY_MODES = ["public", "protected", "private"]


class Property(object):
    """Create a property class to store informations."""

    data_type = None
    _value = "public"
    _visibility = "public"

    default_value = None
    display = True

    editables = ["default_value", "display"]

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
        self.changed = signals.Signal()

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
        return "({}-{}){}:{}".format(
            self.visibility.title(), self.data_type, self.name, self.value
        )

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
        # set the value
        self.value = kwargs.get("value", args[0] if args else self.default_value)
        # create the property's setup
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

        # deserialize the value
        self._deserialize_value(data.pop("value", None))

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
        serialization["value"] = self._serialize_value()

        return serialization

    def copy(self):
        """Copy the property to get a new property with the same attributes.

        Returns:
            Property: The copied property.
        """
        return load(self.name, self.serialize())

    # private methods

    def _deserialize_value(self, value):
        """Deserialize the value in a specific way.

        Arguments:
            value (-): The value of the property to deserialize.
        """
        self.value = value

    def _serialize_value(self):
        """Get the value in a serialized form.

        Returns:
            -: The serialized value.
        """
        return self.value

    # custom methods

    def get_attribute(self, name):
        """Get the value of an attribute of the property.

        Arguments:
            name (str): The name of the attribute to get.

        Returns:
            -: The value of the attribute.
        """
        if name in self.editables:
            return getattr(self, name)
        else:
            MANAGER.project_logger.error(
                "{} object has no attribute '{}'".format(self.__class__.__name__, name)
            )

    def set_attribute(self, name, value):
        """Set the value of an attribute of the property.

        Arguments:
            name (str): The name of the attribute to edit.
            value (-): The value to set to the attribute.
        """
        if name in self.editables:
            setattr(self, name, value)
            self.changed.emit()
        else:
            MANAGER.project_logger.error(
                "{} object has no attribute '{}'".format(self.__class__.__name__, name)
            )

    # properties

    def get_visibility(self):
        """Get the visibility of the property.

        Returns:
            str: The property's visibility
        """
        return self._visibility

    def set_visibility(self, visibility):
        """Set the visibility of the property.

        Arguments:
            visibility (str): The property's visibility.
        """
        if visibility in VISIBILITY_MODES:
            self._visibility = visibility
            self.changed.emit()
        else:
            MANAGER.project_logger.warning(
                "{} isn't a valid visibility mode".format(visibility)
            )

    visibility = property(get_visibility, set_visibility)

    def get_value(self):
        """Get the value of the property.

        Returns:
            -: The value of the property.
        """
        return self._value

    def set_value(self, value):
        """Set the valueof the property.

        Arguments:
            value (-): Thevalue of the property.
        """
        self._value = value
        self.changed.emit()

    value = property(get_value, set_value)


class BoolProperty(Property):
    """Store a bool information."""

    data_type = "bool"
    default_value = ""


class NumericProperty(Property):
    """Store a numeric information."""

    default_value = 0
    min = None
    max = None

    editables = Property.editables + ["min", "max"]

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

    def __getattribute__(self, name):
        """Get an attribute from the value or its parent property.

        Arguments:
            name (str): The name of the attribute or property.

        Returns:
            -: The attribute.
        """
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            return getattr(self.value, name)

    # private methods

    def _deserialize_value(self, value):
        """Deserialize the value in a specific way.

        Arguments:
            value (-): The value of the property to deserialize.
        """
        self.value = properties_values.DictionaryValue(value)
        self.value.parent = self

    # custom methods

    def get_attribute(self, name):
        """Get the value of an attribute of the property.

        Arguments:
            name (str): The name of the attribute to get.

        Returns:
            -: The value of the attribute.
        """
        if "." in name:
            print(name)
            return self.value.get(name)
        return super(DictProperty, self).get_attribute(name)

    def set_attribute(self, name, value):
        """Set the value of an attribute of the property.

        Arguments:
            name (str): The name of the attribute to edit.
            value (-): The value to set to the attribute.
        """
        if "." in name:
            self.value.set(name, value)
            self.changed.emit()
        else:
            super(DictProperty, self).set_attribute(name, value)

    # properties

    def set_value(self, value):
        """Set the valueof the property.

        Arguments:
            value (-): Thevalue of the property.
        """
        self._value = properties_values.DictionaryValue(value)
        self._value.parent = self
        self.changed.emit()

    value = property(Property.get_value, set_value)


class EnumProperty(Property):
    """Store an enum information."""

    data_type = "enum"
    default_value = list()


class CompoundProperty(Property):
    """Store multiple properties information."""

    data_type = "compound"
    default_value = dict()

    # methods

    def create_property(self, data_type, name, *args, **kwargs):
        """Create and add a new property to this member.

        Arguments:
            data_type (str): The property's data type.
            name (str): The name of the property.

        Returns:
            Property: The created property.
        """
        _property = create(data_type, name, *args, **kwargs)
        self.add_property(_property)
        return _property

    def add_property(self, _property):
        """Add a property to the current property.

        Arguments:
            _property (Property): The property to add.
        """
        name = _property.name
        self.value[name] = _property

        # connect the property's signal to this property
        _property.changed.connect(self.changed.emit)

        # emit a signal to stipulate that the property has been changed
        self.changed.emit()

    def get_property(self, name):
        """Get a property object in the compound property.

        Arguments:
            name (str): the name of the property to get.

        Returns:
            Property: The property.
        """
        return self.value.get(name)

    def delete_property(self, name):
        """Delete a property from the member.

        Arguments:
            name (str): The name of the property.
        """
        if name in self.value:
            self.value.pop(name)
            # emit a signal to stipulate that the property has been changed
            self.changed.emit()

    # private methods

    def _deserialize_value(self, value):
        """Deserialize the value in a specific way.

        Arguments:
            value (-): The value of the property to deserialize.
        """
        self.value = dict()
        for name, properties_data in value.items():
            self.add_property(load(name, properties_data))

    def _serialize_value(self):
        """Get the value in a serialized form.

        Returns:
            -: The serialized value.
        """
        serialization = dict()

        for name, _property in self.value.items():
            serialization[name] = _property.serialize()

        return serialization


class MemberProperty(Property):
    """Store a member information."""

    data_type = "member"

    # private methods

    def _deserialize_value(self, value):
        """Deserialize the value in a specific way.

        Arguments:
            value (-): The value of the property to deserialize.
        """
        project = manager.get_project()
        self.value = project.get_member(value) if value else value

    def _serialize_value(self):
        """Get the value in a serialized form.

        Returns:
            str: The serialized value.
        """
        # save the member path
        if self.value:
            return self.value.full_project_path


class CommandsProperty(DictProperty):
    """Store a list of commands."""

    data_type = "commands"
    default_value = dict()

    # methods

    def add_command(self, command, software):
        """Add a command key for a specific software.

        Arguments:
            command (str): The name of the command.
            software (str): the name of the software.

        Returns:
            CommandProperty: The created command property.
        """
        path = "{}.{}".format(software, command)
        cmd = self.value.get(path)
        if cmd is None:
            # create the command and connect its signal to this property
            cmd = commands.Command(command)
            cmd.changed.connect(self.changed.emit)

            # add the command to the property
            self.value.set(path, cmd)

            # emit a signal to stipulate that the property has been changed
            self.changed.emit()
            return cmd

    # private methods

    def _deserialize_value(self, value):
        """Deserialize the value in a specific way.

        Arguments:
            value (-): The value of the property to deserialize.
        """
        self.value = properties_values.DictionaryValue()
        self.value.parent = self

        for software, _commands in value.items():
            for name, command in _commands.items():
                self.value.set(
                    "{}.{}".format(software, name), commands.Command(name, command)
                )

    def _serialize_value(self):
        """Get the value in a serialized form.

        Returns:
            list: The serialized value.
        """
        serialization = dictionaries.Dictionary()

        for software, _commands in self.value.items():
            for name, command in _commands.items():
                serialization.set(
                    "{}.{}".format(software, name),
                    [script.relative_path for script in command],
                )

        return serialization


PROPERTIES_TYPES = {
    "bool": BoolProperty,
    "int": IntProperty,
    "float": FloatProperty,
    "str": StrProperty,
    "list": ListProperty,
    "dict": DictProperty,
    "enum": EnumProperty,
    "compound": CompoundProperty,
    "member": MemberProperty,
    "commands": CommandsProperty,
}


def create(data_type, name, *args, **kwargs):
    """Create a property.

    Arguments:
        data_type (str): The property's data type.
        name (str): The name of the property.
    """
    _property = PROPERTIES_TYPES[data_type]
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
    _property = PROPERTIES_TYPES[data_type]
    _property = _property(name)
    _property.load(data.copy())
    return _property
