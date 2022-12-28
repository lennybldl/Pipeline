"""Manage the package common commands."""

from pipeline.internal import command_calls, manager

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
        list: A list of concept members.
    """
    return MANAGER.project.list_concepts()


def list_abstract_steps(self):
    """List all the existing abstract_steps.

    Returns:
        list: A list of abstract_step members.
    """
    return MANAGER.project.list_abstract_steps()


def list_concrete_steps(self):
    """List all the existing concrete_steps.

    Returns:
        list: A list of concrete_step members.
    """
    return MANAGER.project.list_concrete_steps()


# get available ids


def get_available_concept_id():
    """Get the next available concept id.

    Returns:
        int: The available id.
    """
    return MANAGER.project.get_available_concept_id()


def get_available_abstract_id():
    """Get the next available abstract id.

    Returns:
        int: The available id.
    """
    return MANAGER.project.get_available_abstract_id()


def get_available_concrete_id():
    """Get the next available abstract id.

    Returns:
        int: The available id.
    """
    return MANAGER.project.get_available_concrete_id()


# manipulate members


def call(name, _id):
    """Call a command for a specific concrete step.

    Arguments:
        name (str): The name of the command.
        _id (int): The id of the concrete step.
    """
    # get the commands to call
    rules = get_rules(_id)
    commands = rules.get("{}.{}".format(name, DATABASE.software), dict())
    commands = commands.get("commands", list())

    # call the commands
    for command in commands:
        if command.endswith(".py"):
            command_calls.call_python_command(command, _id)


# get members informations


def get_step_data(_id):
    """Get the concrete and abstract data of a concrete step.

    Arguments:
        _id (int): The id of the concrete step.

    Returns:
        tuple: The concrete data and the abstract data.
    """
    _id = get_concrete_step_id(_id)
    return _id.get_data()


def get_step_path(_id, relative=False):
    """Get the path of a concrete step.

    Arguments:
        _id (int): The id of the concrete step.

    Keyword Arguments:
        relative (bool, optional): To get the path relative to the project's path.
            Default to False.

    Returns:
        str: The step's path.
    """
    _id = get_concrete_step_id(_id)
    return _id.get_path(relative)


def get_abstract_step_path(_id, relative=True):
    """Get the abstract path of a abstract step.

    Arguments:
        _id (int): The abstract step id to get the abstract path from.

    Keyword Arguments:
        relative (bool, optional): To get the path relative to the project's path.
            Default to True.

    Returns:
        str: The unformated procedural path of the abstract step.
    """
    _id = get_abstract_step_id(_id)
    return _id.get_abstract_path(relative=relative)


def get_step_name(_id):
    """Get a concrete step's name.

    Arguments:
        _id (int): The id of the concrete step.

    Returns:
        str: The name of the step.
    """
    _id = get_concrete_step_id(_id)
    return _id.get_name()


def get_rules(step):
    """Get the rules that can be performed on a abstract step id or a concept id.

    Arguments:
        step (str, int): The id to get the rules from.
            If it's an integer, the abstract step id.
            If it's a string, the concept id written "cId".

    Returns:
        list: A list of rules names.
    """
    project = DATABASE.project
    if isinstance(step, str):
        member = project.get_concept_id(step.replace("c", ""))
    else:
        member = project.get_abstract_step_id(step)
    return member.get_rules()


def get_root_concept(_id):  # TODO : USELESS?
    """Get the root concept of a abstract step.

    Arguments:
        _id (int): The id of the abstract step.

    Returns:
        int: The id of the root concept.
    """

    def recursively_find_root_concept(_id):
        """Get if the abstract id's concept is in the root concept.

        If not, try it's parent.

        Arguments:
            _id (int): The id of the abstract step.

        Returns:
            int: The id of the root concept.
        """
        if project.get("abstract.id.{}.concept".format(_id)) in root_concepts:
            _id = recursively_find_root_concept(
                project.get("abstract.id.{}.parent".format(_id))
            )
        return _id

    project = DATABASE.project
    root_concepts = database.ROOT_CONCEPTS
    return recursively_find_root_concept(_id)
