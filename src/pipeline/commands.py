"""Manage the package common commands."""

from pipeline.internal import manager

MANAGER = None


def start(software):
    """Start the pipeline withoud any UI.

    Arguments:
        software (str): The software we're executing the pipeline in.
    """
    global MANAGER
    MANAGER = manager.Manager(software=software)


# edit project


def load_project(path):
    """Load a project from a specific path.

    Arguments:
        path (str): The path to the project.
    """
    MANAGER.load_project(path)


def create_project(path):
    """Create the project folder and initialize.

    Arguments:
        path (str): The path to create the pipeline to.
    """
    MANAGER.create_project(path)


def save():
    """Save the current project pipeline."""
    MANAGER.project.save()


# add members


def add_concept(*args, **kwargs):
    """Add a concept to the project.

    Returns:
        Concept: The id of the added concept.
    """
    return MANAGER.project.add_concept(*args, **kwargs)


def add_abstract_step(*args, **kwargs):
    """Add a abstract step to the project.

    Returns:
        AbstractStep: The id of the added abstract step.
    """
    return MANAGER.project.add_abstract_step(*args, **kwargs)


def add_concrete_step(*args, **kwargs):
    """Add a concrete step to the project.

    Arguments:
        abstract_id (str): The id of the abstract step this step belongs to.

    Returns:
        int: The id of the added concrete step.
    """
    return MANAGER.project.add_concrete_step(*args, **kwargs)


# get existing members


def get_concept(_id):
    """Get an existing concept from its id.

    Arguments:
        _id (int): The concept's id.

    Returns:
        Concept: The concept.
    """
    return MANAGER.project.get_concept(_id)


def get_abstract_step(_id):
    """Get an existing abstract step from its id.

    Arguments:
        _id (int): The abstract step's id.

    Returns:
        AbstractStep: The abstract step.
    """
    return MANAGER.project.get_abstract_step(_id)


def get_concrete_step(_id):
    """Get an existing concrete step from its id.

    Arguments:
        _id (int): The concrete step's id.

    Returns:
        ConcreteStep: The concrete step.
    """
    return MANAGER.project.get_concrete_step(_id)


def list_concepts():
    """List all the existing concepts.

    Returns:
        list: A list of Concept members.
    """
    return MANAGER.project.list_concepts()


def list_abstract_steps():
    """List all the existing abstract_steps.

    Returns:
        list: A list of AbstractStep members.
    """
    return MANAGER.project.list_abstract_steps()


def list_concrete_steps():
    """List all the existing concrete_steps.

    Returns:
        list: A list of ConcreteStep members.
    """
    return MANAGER.project.list_concrete_steps()


# manipulate members


def call(member, name):
    """Call a command for a specific member.

    Arguments:
        member (Member, str): The member to work on. It can either be
            a Member instance or the full path of the member in the project.
        name (str): The name of the command.
    """
    if isinstance(member, str):
        member = MANAGER.project.get_member(member)
    member.call(name)


def add_property(member, data_type, name, *args, **kwargs):
    """Get a property on a specific member.

    Arguments:
        member (Member, str): The member to work on. It can either be
            a Member instance or the full path of the member in the project.
        data_type (str): The property's data type.
        name (str): The name of the property to add.

    Returns:
        Property: The desired property's value.
    """
    if isinstance(member, str):
        member = MANAGER.project.get_member(member)
    return member.add_property(data_type, name, *args, **kwargs)


def get_property(member, name):
    """Get a property on a specific member.

    Arguments:
        member (Member, str): The member to work on. It can either be
            a Member instance or the full path of the member in the project.
        name (str): The name of the property to get.

    Returns:
        -: The desired property's value.
    """
    if isinstance(member, str):
        member = MANAGER.project.get_member(member)
    return getattr(member, name)


def set_property(member, name, value):
    """Set a property's value on a specific member.

    Arguments:
        member (Member, str): The member to work on. It can either be
            a Member instance or the full path of the member in the project.
        name (str): The name of the property to set.
        value (-): the value to set

    Returns:
        -: The desired property's value.
    """
    if isinstance(member, str):
        member = MANAGER.project.get_member(member)
    return setattr(member, name, value)
