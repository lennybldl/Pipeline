"""Manage the rig tools."""

import os

from python_core.types import strings

from pipeline.api.maya_api import maya_asset
from pipeline.utils import database

ASSET = maya_asset.MayaAsset()
DATABASE = database.Database()


# rig methods


def update_model():
    """Update the model in the rig file.

    It only will import the last modeling published version.
    """

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # make sure we're on a rig task
    if task != "rig":
        raise RuntimeError("# Pipeline : The update model only works on rig tasks")

    # figure out the path to the path to the modeling publish
    path = ASSET.get_path_from_name(asset_name)
    path = os.path.join(path, "modeling", "export", asset_name + ".fbx")

    # check if the modeling publish exists
    if not os.path.exists(path):
        print("# Pipeline : The modeling export doesn't seem to exist -> " + path)
        return

    # if a GEO group exists : delete it
    if cmds.objExists("GEO"):
        cmds.delete("GEO")

    # import the modeling publish
    cmds.file(
        path,
        i=True,
        type="FBX",
        ignoreVersion=True,
        mergeNamespacesOnClash=False,
        renamingPrefix=asset_name,
        options="fbx",
        preserveReferences=True,
        importTimeRange="combine",
    )

    print("# Pipeline : Model imported -> " + path)


def set_joints_to_export():
    """Save the selected joints in the pipe node to know wich ones to export to unreal."""  # noqa E501

    from maya import cmds

    # get pipenode from data
    app_data = DATABASE.app_data

    # get the pipe node of the current task
    pipe_node = app_data["tasks"]["rig"]["pipe_node"]

    # save the selection in the pipe node
    cmds.setAttr(pipe_node + ".JointsToExport", lock=False)
    cmds.setAttr(
        pipe_node + ".JointsToExport", map(str, cmds.ls(sl=True)), type="string"
    )
    cmds.setAttr(pipe_node + ".JointsToExport", lock=True)

    # print a debug
    print("# Pipeline : Joints to export set in " + pipe_node)


def select_joints_to_export(pipe_node=None, add=False):
    """Select the selected joints saved in the pipe node.

    :param pipe_node: The pipe node to select the joints from
    :type pipe_node: str
    :param add: Wether or not to add the joints to the current selection
    :type add: bool
    """

    from maya import cmds

    # get pipenode from data
    app_data = DATABASE.app_data

    # get the pipe node of the current task if not specifyied
    if pipe_node is None:
        pipe_node = app_data["tasks"]["rig"]["pipe_node"]

    # get the joints to export
    joints = cmds.getAttr(pipe_node + ".JointsToExport")

    if not joints:
        cmds.select(pipe_node, add=add)
        return

    # select the joints to export
    joints = strings.remove_specials(str(joints), ignore=list(",|_"))
    joints = joints.split(",")

    # select the joints
    asset_namespace = pipe_node.rpartition(":")[0]
    cmds.select(
        [
            "{}:{}".format(asset_namespace, joint).replace(
                "|", "|{}:".format(asset_namespace)
            )
            for joint in joints
        ],
        add=add,
    )
