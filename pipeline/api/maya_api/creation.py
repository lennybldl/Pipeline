"""Manage the maya files creation."""

import os
import sys

from pipeline.api.maya_api import maya_asset
from pipeline.api.maya_api.tools import rig
from pipeline.ui.dialogs import popups
from pipeline.utils import database

ASSET = maya_asset.MayaAsset()
DATABASE = database.Database()

ATTRIBUTES = [".tx", ".ty", ".tz", ".rx", ".ry", ".rz", ".sx", ".sy", ".sz", ".v"]


def create_maya_scenes(name):
    """Create a specific maya scene from path.

    :param name: The asset name
    :type name: str

    :return: The complete path to the create file
    :rtype: str
    """

    from maya import cmds

    # save the current file before
    popups.save_popup()

    # get scene infromations and extract useful data
    informations = ASSET.get_informations_from_name(name)
    asset_type, basename, task, version, comment, path = informations

    # create a new file to the new name
    cmds.file(new=True, force=True)
    cmds.file(rename=os.path.join(path, name))

    # Create a correct organisation
    if version == 0:
        # initialize the asset task
        method = getattr(sys.modules[__name__], task + "_creation")
        method()

    # save the file
    cmds.file(save=True, type="mayaAscii", force=True)

    return os.path.join(path, name)


# pipe node


def initialize_pipe_node():
    """Create the pipe node that will be used to keep track of scenes.

    :return: The pipe node
    :rtype: str
    """

    from maya import cmds

    # get pipenode from data
    app_data = DATABASE.app_data

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the pipe node of the current task
    pipe_node = app_data["tasks"][task]["pipe_node"]

    # lock the pipe node attributes
    for attr in ATTRIBUTES:
        cmds.setAttr(pipe_node + attr, lock=True, keyable=False, channelBox=False)

    # add tracking attributes
    cmds.addAttr(pipe_node, longName="AssetName", dataType="string")
    cmds.addAttr(pipe_node, longName="AssetVersion", attributeType="short", min=0)
    cmds.addAttr(pipe_node, longName="Comment", dataType="string")

    if task == "rig":
        cmds.addAttr(
            pipe_node,
            longName="JointsToExport",
            dataType="string",
        )
        cmds.setAttr(pipe_node + ".JointsToExport", lock=True)

    elif task == "animation":
        cmds.addAttr(
            pipe_node,
            longName="BakeScene",
            attributeType="bool",
        )
        cmds.setAttr(pipe_node + ".BakeScene", lock=True)

    # fill up the attributes
    cmds.setAttr(pipe_node + ".AssetName", asset_name, type="string")

    # lock the tracking attributes
    for attr in [".AssetName", ".Comment", ".AssetVersion"]:
        cmds.setAttr(pipe_node + attr, lock=True)

    return pipe_node


def update_pipe_node():
    """Update the pipe node with the new informations."""

    from maya import cmds

    # get pipenode from data
    app_data = DATABASE.app_data

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations

    # get the pipe node of the current task
    pipe_node = app_data["tasks"][task]["pipe_node"]

    # set the version attr
    cmds.setAttr(pipe_node + ".AssetVersion", lock=False)
    cmds.setAttr(pipe_node + ".AssetVersion", version)
    cmds.setAttr(pipe_node + ".AssetVersion", lock=True)

    # set the comment attr
    cmds.setAttr(pipe_node + ".Comment", lock=False)
    cmds.setAttr(pipe_node + ".Comment", comment or "", type="string")
    cmds.setAttr(pipe_node + ".Comment", lock=True)

    # save the file
    cmds.file(save=True, type="mayaAscii", force=True)


# tasks creation


def modeling_creation():
    """Actions to perform at the modeling scene creation."""

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # create a GEO group inside a group named after the asset
    geo_group = cmds.group(empty=True, name="GEO")
    cmds.group(geo_group, name=asset_name)

    # add attributes on the GEO group to keep track of informations
    initialize_pipe_node()


def rig_creation():
    """Actions to perform at the rig scene creation."""

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # create an empty rig group to store all the rig
    cmds.group(cmds.group(empty=True, name="RIG"), name=asset_name)

    # add attributes on the RIG group to keep track of informations
    initialize_pipe_node()

    # import the last modeling version
    rig.update_model()


def layout_creation():
    """Actions to perform at the layout scene creation."""

    from maya import cmds

    # create groups for the layout
    cmds.group(empty=True, name="LAYOUT")

    # add attributes on the RIG group to keep track of informations
    initialize_pipe_node()


def animation_creation():
    """Actions to perform at the animation scene creation."""

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # create empty groups
    groups = list()
    groups.append(cmds.group(empty=True, name="pipe_node"))
    groups.append(cmds.group(empty=True, name="CAMERAS"))
    groups.append(cmds.group(empty=True, name="LIGHTS"))
    groups.append(cmds.group(empty=True, name="ANIMATED"))
    groups.append(cmds.group(empty=True, name="LAYOUT"))
    cmds.group(groups, name=asset_name)

    # save the file with the empty groups
    cmds.file(save=True, type="mayaAscii", force=True)

    # add attributes on the RIG group to keep track of informations
    initialize_pipe_node()


def cleaning_creation():
    """Actions to perform at the cleaning scene creation."""

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # create empty groups
    groups = list()
    groups.append(cmds.group(empty=True, name="pipe_node"))
    cmds.group(groups, name=asset_name)

    # save the file with the empty groups
    cmds.file(save=True, type="mayaAscii", force=True)

    # add attributes on the RIG group to keep track of informations
    initialize_pipe_node()


# runtime creations


def increment_save(comment=None):
    """Save the current file as an increment of the current scene.

    :param comment: A comment to know a bit more about the file
    :type comment: str
    """
    from maya import cmds

    # save the file before
    popups.save_popup()

    # get the path to the files
    task_path = os.path.dirname(cmds.file(q=True, sceneName=True))

    # get the latest file
    latest_file = ASSET.get_latest_file(task_path, ".ma")

    # get scene infromations and extract useful data
    informations = ASSET.get_informations_from_name(latest_file)
    asset_type, basename, task, version, asset_comment, path = informations

    # deduce the asset task name to create it
    asset_name = ASSET.get_asset_name(asset_type, basename)
    asset_task_name = ASSET.get_asset_task_name(asset_name, task)
    if comment is None:
        file_name = "_".join([asset_task_name, str(version + 1).zfill(3)])
    else:
        file_name = "_".join([asset_task_name, str(version + 1).zfill(3), comment])

    # get the full path to the new incremented file
    path = os.path.join(task_path, file_name + ".ma").replace("/", "\\")

    # create the scene
    cmds.file(rename=path)
    cmds.file(save=True, type="mayaAscii", force=True)
    print("# Pipeline : File incremented -> " + path)

    # update pipe_node
    update_pipe_node()
    print("# Pipeline : Pipe node updated")

    # save the opend file as a recently opend file
    ASSET.update_recents(os.path.basename(path))


def create_bake_file():
    """Create the bake file to bake the animations and export them."""

    from maya import cmds

    # get pipenode from data
    app_data = DATABASE.app_data

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the pipe node of the current task
    pipe_node = app_data["tasks"][task]["pipe_node"]
    if cmds.getAttr(pipe_node + ".BakeScene"):
        print("# Pipeline : Bake file not created -> you already are in a bake file.")
        return

    if comment:
        comment += "_bake.ma"
    else:
        comment = "bake.ma"

    # get the baking file name
    bake_file = "_".join(
        [
            ASSET.get_asset_task_name(asset_name, task),
            str(version).zfill(3),
            comment,
        ]
    )

    path = os.path.join(path, bake_file)
    cmds.file(save=True, type="mayaAscii", force=True)
    cmds.file(rename=path)
    cmds.file(save=True, type="mayaAscii", force=True)

    # set the bake scene attr to true to specify that we're in a bake scene
    cmds.setAttr(pipe_node + ".BakeScene", lock=False)
    cmds.setAttr(pipe_node + ".BakeScene", True)
    cmds.setAttr(pipe_node + ".BakeScene", lock=True)

    # save the file
    cmds.file(save=True, type="mayaAscii", force=True)

    print("# Pipeline : Bake file created -> " + path)
