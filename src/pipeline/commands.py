"""Manage the package common commands."""
import os
import sys

from python_core.types import dictionaries, items, strings

from pipeline import database

DATABASE = database.Database(software="windows", py_version=3)

# Use different modules to import modules considering the python version
if DATABASE.py_version == 2:
    import imp
else:
    import importlib.util

# edit project


def initialize(path):
    """Initialize the pipeline on a specific path.

    Arguments:
        path (str): The path to the project.
    """
    # create the .pipeline folder if it doesn't exist
    path = items.Folder(path)
    if not path.get_folder(".pipeline").exists():
        create_project(path)

    # initialize the database
    DATABASE.path = path
    DATABASE.logger.add_file_handler(DATABASE.log_path, mode="w")


def create_project(path):
    """Create the project folder and initialize it's pipeline.

    Arguments:
        path (str): The path to create the pipeline to.
    """
    # create the project folder
    project_path = items.Folder(path)
    project_path.create()

    # create the pipeline folder for the project
    pipeline_path = items.Folder(database.RESSOURCES).get_folder(".pipeline")
    pipeline_path.copy(project_path.get_folder(".pipeline"))

    # initialize the database
    initialize(path)


def add_abstract_step(_type, parent, **properties):
    """Add an abstract step to the config.

    Arguments:
        _type (str): The type of step. ("asset", "task").
        parent (int): The id of the parent of this step.

    Returns:
        int: The id of the added abstract step.
    """
    config = DATABASE.config

    # set default values for an abstract step
    _id = get_available_abstract_id()
    properties["type"] = _type
    properties["parent"] = parent
    properties["name"] = properties.get("name", "{}{}".format(_type, _id) + "_{index}")
    if _type == "task":
        properties["task"] = properties.get("task", "{}{}".format(_type, _id))

    # add the rules for the abstract step
    rules = properties.get("rules")
    if rules is None:
        properties["rules"] = {"_same_as_": [_type]}

    # write the new config
    config.set("abstract.id.{}".format(_id), properties)
    DATABASE.config = config

    return _id


def add_concrete_step(abstract_id, parent, **properties):
    """Add a concrete step to the config.

    Arguments:
        abstract_id (str): The id of the abstract step this step belongs to.
        parent (int): The id of the parent of this step.

    Returns:
        int: The id of the added concrete step.
    """
    config = DATABASE.config

    # set default values for a concrete step
    _id = get_available_concrete_id()
    properties["abstract_id"] = abstract_id
    properties["parent"] = parent
    properties["basename"] = properties.get("basename", "")
    properties["index"] = properties.get("index")
    properties["comment"] = properties.get("comment", "")

    # write the new config
    config.set("concrete.id.{}".format(_id), properties)
    DATABASE.config = config
    config.set(
        "concrete.path.{}".format(get_step_path(_id, relative=True)), {"id": _id}
    )
    DATABASE.config = config

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
    commands = commands.get("commands")

    # call the commands
    for command in commands:
        command = DATABASE.rules_path.get_file(command)

        # import the module
        if DATABASE.py_version == 2:
            module = imp.load_source(command.name, command.path)
        else:
            spec = importlib.util.spec_from_file_location(
                command.name.replace(".py", ""), command.path
            )
            module = importlib.util.module_from_spec(spec)
            sys.modules[spec.name] = module
            spec.loader.exec_module(module)

        # execute the module
        if hasattr(module, "execute"):
            module.execute(_id)
        else:
            DATABASE.logger.warning(
                "Could not find an 'execute' function in '{}'".format(command)
            )


# get available ids


def get_available_abstract_id():
    """Get the next available abstract id.

    Returns:
        int: The available id.
    """
    config = DATABASE.config
    existing_ids = list(map(int, config.get("abstract.id").keys()))
    potential_ids = set(range(1, len(existing_ids) + 2))
    return list(potential_ids - set(existing_ids))[0]


def get_available_concrete_id():
    """Get the next available abstract id.

    Returns:
        int: The available id.
    """
    config = DATABASE.config
    existing_ids = list(map(int, config.get("concrete.id").keys()))
    potential_ids = set(range(1, len(existing_ids) + 2))
    return list(potential_ids - set(existing_ids))[0]


# get step informations


def get_step_data(_id):
    """Get the concrete and abstract data of a concrete step.

    Arguments:
        _id (int): The id of the concrete step.

    Returns:
        tuple: The concrete data and the abstract data.
    """
    config = DATABASE.config

    # get the concrete and abstract data of a concrete step
    concrete_data = config.get("concrete.id.{}".format(_id))
    abstract_id = concrete_data.get("abstract_id")
    abstract_data = config.get("abstract.id.{}".format(abstract_id))

    return concrete_data, abstract_data


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

    def recursively_get_path(_id):
        """Recursively get the name of each parent of a step.

        Arguments:
            _id (int): The step's id.

        Returns:
            _type_: _description_.
        """
        # get useful datas
        concrete_data = get_step_data(_id)[0]

        path = [get_step_name(_id)]
        parent_id = concrete_data.get("parent")
        if parent_id == 0:
            if not relative:
                path.append(DATABASE.path)
        else:
            path.extend(recursively_get_path(parent_id))

        return path

    # return the formated path
    return os.path.join(*reversed(recursively_get_path(_id)))


def get_step_name(_id):
    """Get a concrete step's name.

    Arguments:
        _id (int): The id of the concrete step.

    Returns:
        str: The name of the step.
    """
    # get useful datas
    config = DATABASE.config
    concrete_data, abstract_data = get_step_data(_id)
    name = abstract_data.get("name")

    # process index
    padding = abstract_data.get("index_padding", config.get("abstract.index_padding"))
    index = str(concrete_data.get("index")).zfill(padding)

    # process parent name
    parent_name = None
    if "{parent}" in name:
        parent_id = concrete_data.get("parent")
        if parent_id == 0:
            parent_name = DATABASE.project_name
        else:
            parent_name = get_step_name(parent_id)

    # process task name
    task_name = None
    if "{task}" in name:
        parent_id = concrete_data.get("parent")
        if parent_id != 0:
            task_name = get_step_data(parent_id)[1].get("task")

    # process asset name
    asset_name = None
    if "{asset}" in name:
        parent_id = concrete_data.get("parent")
        while True:
            # if the step is child of the root it can not have a parent asset
            if parent_id == 0:
                asset_name = None
                break
            # get the parent asset
            parent_concrete_data, parent_abstract_data = get_step_data(parent_id)
            if parent_abstract_data.get("type") == "asset":
                asset_name = get_step_name(parent_id)
                break
            parent_id = parent_concrete_data.get("parent")

    # match the variables and the values to replace them with
    match = {
        "{project}": DATABASE.project_name,
        "{parent}": parent_name,
        "{asset}": asset_name,
        "{task}": task_name,
        "{basename}": concrete_data.get("basename"),
        "{index}": index,
        "{comment}": concrete_data.get("comment"),
        "{extension}": concrete_data.get("extension"),
    }

    # replace the variables in the path with the matching values
    # and get rid of double underscores
    name = strings.replace(abstract_data.get("name"), match.keys(), match.values())
    while "__" in name:
        name = name.replace("__", "_")
    return name


def get_rules(step):
    """Get the rules that can be performed on a particular step type or abstract id.

    Arguments:
        step (str, int): The name of the step type to get the rules from
            or the id of an abstract step.

    Returns:
        list: A list of rules names.
    """
    config = DATABASE.config

    # get the rules either from a step type of an abstract step id
    if isinstance(step, str):
        rules_path = "abstract.rules.{}".format(step)
    else:
        rules_path = "abstract.id.{}.rules".format(step)

    # get the rules dictionary
    rules_dict = config.get(rules_path)
    rules = dictionaries.OrderedDictionary()
    for rule_name, values in rules_dict.items():
        # get the rules from an other step rules
        if rule_name == "_same_as_":
            for rule in values:
                rules.update(get_rules(rule))
        # get the rules of the current step
        else:
            rules[rule_name] = values
    return rules


def get_abstract_step_path(_id, relative=True):
    """Get the abstract path of an abstract step.

    Arguments:
        _id (int): The abstract step id to get the abstract path from.

    Keyword Arguments:
        relative (bool, optional): To get the path relative to the project's path.
            Default to True.

    Returns:
        str: The unformated procedural path of the abstract step.
    """
    # figure out the path where to store the step from its id
    config = DATABASE.config

    step_path = [DATABASE.path]
    parent_id = _id
    while True:
        step_path.insert(-1, config.get("abstract.id.{}.name".format(parent_id)))
        parent_id = config.get("abstract.id.{}.parent".format(parent_id))
        if parent_id == 0:
            break

    # ignore the project path if we want a relative path
    if relative:
        step_path.pop(-1)

    return os.path.join(*reversed(step_path))
