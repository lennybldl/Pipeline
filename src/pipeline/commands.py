"""Manage the package common commands."""

from python_core.types import items

from pipeline.api import concrete_steps, members, abstract_steps
from pipeline.internal import command_calls, database

DATABASE = None


def start(software):
    """Start the pipeline withoud any UI.

    Arguments:
        software (str): The software we're executing the pipeline in.
    """
    global DATABASE
    DATABASE = database.Database(software=software)


# edit project


def initialize(path):
    """Initialize the pipeline on a specific path.

    Arguments:
        path (str): The path to the project.
    """
    # create the .pipeline folder if it doesn't exist
    path = items.Folder(path)
    if not path.get_folder(".pipeline").exists():
        create_pipeline(path)

    # initialize the database
    DATABASE.path = path
    DATABASE.logger.add_file_handler(DATABASE.log_path, mode="w")


def create_pipeline(path):
    """Create the pipeline folder and initialize.

    Arguments:
        path (str): The path to create the pipeline to.
    """
    # create the project folder
    project_path = items.Folder(path)
    project_path.create()

    # create the pipeline folder for the project
    pipeline_path = database.RESOURCES.get_folder(".pipeline")
    pipeline_path.copy(to=project_path.get_folder(".pipeline"))

    # initialize the database
    initialize(path)


def add_concept(name, **properties):
    """Add a concept to the config.

    Arguments:
        name (str): The name to give to the concept.

    Returns:
        Concept: The id of the added concept.
    """
    _id = get_available_concept_id()
    _id = members.Concept(_id)
    _id.add(name, **properties)
    return _id


def add_abstract_step(_type, parent, **properties):
    """Add a abstract step to the config.

    Arguments:
        _type (str): The type of step it is. (asset, task, workfile).
        parent (int): The id of the parent of this step.

    Returns:
        AbstractStep: The id of the added abstract step.
    """
    _id = get_available_abstract_id()
    _id = abstract_steps.ABSTRACT_STEPS.get(_type)(_id)
    _id.add(parent=parent, **properties)
    return _id


def add_concrete_step(abstract_id, parent, **properties):
    """Add a concrete step to the config.

    Arguments:
        abstract_id (str): The id of the abstract step this step belongs to.
        parent (int): The id of the parent of this step.

    Returns:
        int: The id of the added concrete step.
    """
    _id = get_available_concrete_id()
    abstract_id = DATABASE.config.get_abstract_step_id(abstract_id)
    _id = concrete_steps.CONCRETE_STEPS.get(abstract_id.type)(_id)
    _id.add(abstract_id=abstract_id, parent=parent, **properties)
    return _id


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


# get available ids


def get_available_concept_id():
    """Get the next available concept id.

    Returns:
        int: The available id.
    """
    existing_ids = list(map(int, DATABASE.config.get("concept.id").keys()))
    potential_ids = set(range(1, len(existing_ids) + 2))
    return list(potential_ids - set(existing_ids))[0]


def get_available_abstract_id():
    """Get the next available abstract id.

    Returns:
        int: The available id.
    """
    existing_ids = list(map(int, DATABASE.config.get("abstracts.id").keys()))
    potential_ids = set(range(1, len(existing_ids) + 2))
    return list(potential_ids - set(existing_ids))[0]


def get_available_concrete_id():
    """Get the next available abstract id.

    Returns:
        int: The available id.
    """
    existing_ids = list(map(int, DATABASE.config.get("concretes.id").keys()))
    potential_ids = set(range(1, len(existing_ids) + 2))
    return list(potential_ids - set(existing_ids))[0]


# get existing ids


def get_concept_id(_id):
    """Get an existing concept id.

    Arguments:
        _id (int): The concept's id.

    Returns:
        Concept: The concept.
    """
    return DATABASE.config.get_concept_id(_id)


def get_abstract_step_id(_id):
    """Get an existing abstract step id.

    Arguments:
        _id (int): The abstract step's id.

    Returns:
        AbstractStep: The abstract step.
    """
    return DATABASE.config.get_abstract_step_id(_id)


def get_concrete_step_id(_id):
    """Get an existing concrete step id.

    Arguments:
        _id (int): The concrete step's id.

    Returns:
        ConcreteStep: The concrete step.
    """
    return DATABASE.config.get_concrete_step_id(_id)


# get step informations


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
    config = DATABASE.config
    if isinstance(step, str):
        member = config.get_concept_id(step.replace("c", ""))
    else:
        member = config.get_abstract_step_id(step)
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
        if config.get("abstracts.id.{}.concept".format(_id)) in root_concepts:
            _id = recursively_find_root_concept(
                config.get("abstracts.id.{}.parent".format(_id))
            )
        return _id

    config = DATABASE.config
    root_concepts = database.ROOT_CONCEPTS
    return recursively_find_root_concept(_id)
