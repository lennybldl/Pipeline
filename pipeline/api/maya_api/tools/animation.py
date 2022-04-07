"""Manage the layout / animation tools."""

import os

from pipeline.api.maya_api import maya_asset
from pipeline.api.maya_api.tools import rig
from pipeline.utils import database

ASSET = maya_asset.MayaAsset()
DATABASE = database.Database()

# layout methods


def import_reference(asset_name, times=1):
    """Import an asset as reference multiple times.

    :param asset_name: The name of the asset to import.
    :type asset_name: str
    :param times: The number of times to import the asset
    :type times: int
    """

    from maya import cmds

    # get the asset path from the asset name
    path = ASSET.get_path_from_name(asset_name)

    # get the file to import
    export = os.path.join(path, "rig", "export", asset_name + ".ma")
    if os.path.exists(export):
        path = export
        file_type = "mayaAscii"
    else:
        export = os.path.join(path, "modeling", "export", asset_name + ".fbx")
        if os.path.exists(export):
            path = export
            file_type = "FBX"
        else:
            export = os.path.join(path, "cleaning", "export", asset_name + ".ma")
            if os.path.exists(export):
                path = export
                file_type = "mayaAscii"
            else:
                raise ValueError(
                    "# Pipeline : No maya export found for {} ".format(asset_name)
                    + "in modeling, cleaning or rig."
                )

    # import the asset as reference
    for _ in range(times):
        cmds.file(
            path,
            reference=True,
            type=file_type,
            ignoreVersion=True,
            groupLocator=True,
            mergeNamespacesOnClash=False,
            namespace=asset_name,
            options="v=0;",
        )

    print("# Pipeline : Imported {}x -> {}".format(times, path))


# animation methods


def get_exportable_animateds(pipe_nodes=None):
    """Get all the assets in the current animation scene with a rig pipe node group.

    :param pipe_nodes: A list of pipe nodes to get the joints to export from
    :type pipe_nodes: list, none
    """

    from maya import cmds

    # get pipenode from data
    app_data = DATABASE.app_data

    if pipe_nodes is None:
        pipe_node = app_data["tasks"]["rig"]["pipe_node"]
        pipe_nodes = cmds.ls("*:" + pipe_node)

    animateds = dict()
    for pipe_node in pipe_nodes:
        animateds.update(
            {
                pipe_node.rpartition(":")[0]: {
                    "asset_name": cmds.getAttr(pipe_node + ".AssetName"),
                },
            }
        )

    return animateds


def bake_animations(pipe_nodes=None):
    """Bake the animations of all the specifyied assets.

    :param pipe_nodes: A list of pipe_nodes to get the joints to export from.
        If none, bake all.
    :type pipe_nodes: list, none

    :return: The dictionnary of assets to export
    :rtype: dict
    """

    from maya import cmds

    # get assets to export
    animateds = get_exportable_animateds(pipe_nodes)

    # bake the animations
    cmds.select(clear=True)
    for asset_namespace in animateds.keys():
        # select all the joints to bake
        rig.select_joints_to_export(asset_namespace + ":RIG", add=True)

    # bake them
    cmds.bakeResults(
        cmds.ls(sl=True),
        simulation=True,
        time=(
            cmds.playbackOptions(q=True, min=True),
            cmds.playbackOptions(q=True, max=True),
        ),
        sampleBy=1,
    )

    return animateds


# TODO : delete this method (specific to welcome aboard) from the pipe

TO_UNBIND = [
    "Hips_jnt",
    "Spine_jnt",
    "Spine1_jnt",
    "Spine2_jnt",
    "Spine3_jnt",
    "Neck_jnt",
    "Neck1_jnt",
    "Head_jnt",
    "LeftShoulder_jnt",
    "LeftArm_jnt",
    "LeftForeArm_jnt",
    "LeftHand_jnt",
    "LeftHandThumb1_jnt",
    "LeftHandThumb2_jnt",
    "LeftHandThumb3_jnt",
    "LeftHandThumb4_jnt",
    "LeftInHandIndex_jnt",
    "LeftHandIndex1_jnt",
    "LeftHandIndex2_jnt",
    "LeftHandIndex3_jnt",
    "LeftHandIndex4_jnt",
    "LeftInHandMiddle_jnt",
    "LeftHandMiddle1_jnt",
    "LeftHandMiddle2_jnt",
    "LeftHandMiddle3_jnt",
    "LeftHandMiddle4_jnt",
    "LeftInHandRing_jnt",
    "LeftHandRing1_jnt",
    "LeftHandRing2_jnt",
    "LeftHandRing3_jnt",
    "LeftHandRing4_jnt",
    "LeftInHandPinky_jnt",
    "LeftHandPinky1_jnt",
    "LeftHandPinky2_jnt",
    "LeftHandPinky3_jnt",
    "LeftHandPinky4_jnt",
    "RightShoulder_jnt",
    "RightArm_jnt",
    "RightForeArm_jnt",
    "RightHand_jnt",
    "RightHandThumb1_jnt",
    "RightHandThumb2_jnt",
    "RightHandThumb3_jnt",
    "RightHandThumb4_jnt",
    "RightInHandIndex_jnt",
    "RightHandIndex1_jnt",
    "RightHandIndex2_jnt",
    "RightHandIndex3_jnt",
    "RightHandIndex4_jnt",
    "RightInHandMiddle_jnt",
    "RightHandMiddle1_jnt",
    "RightHandMiddle2_jnt",
    "RightHandMiddle3_jnt",
    "RightHandMiddle4_jnt",
    "RightInHandRing_jnt",
    "RightHandRing1_jnt",
    "RightHandRing2_jnt",
    "RightHandRing3_jnt",
    "RightHandRing4_jnt",
    "RightInHandPinky_jnt",
    "RightHandPinky1_jnt",
    "RightHandPinky2_jnt",
    "RightHandPinky3_jnt",
    "RightHandPinky4_jnt",
    "LeftUpLeg_jnt",
    "LeftLeg_jnt",
    "LeftFoot_jnt",
    "LeftToeBase_jnt",
    "LeftToeBaseEnd_jnt",
    "RightUpLeg_jnt",
    "RightLeg_jnt",
    "RightFoot_jnt",
    "RightToeBase_jnt",
    "RightToeBaseEnd_jnt",
]


def disconnect_rig_from_mocap():
    """Disconnect the selected character from it's connected mocap."""

    from maya import cmds

    # get the selected objects
    character = cmds.ls(sl=True)[0]

    # figure out the namespace
    character_namespace = "".join(character.rpartition(":")[0:2])

    for joint_name in TO_UNBIND:

        # figure out the joint name
        joint = ":".join([character_namespace, joint_name])

        if not cmds.objExists(joint):
            continue

        try:
            # break rotate connections
            connected = cmds.listConnections(
                joint + ".rotate",
                source=1,
                plugs=1,
                type="joint",
            )
            if connected:
                cmds.disconnectAttr(connected[0], joint + ".rotate")
                cmds.setAttr(joint + ".rotate", 0, 0, 0)

            # break translate connections
            if joint_name == "Hips_jnt":
                connected = cmds.listConnections(
                    joint + ".translate",
                    source=1,
                    plugs=1,
                    type="joint",
                )
                if connected:
                    cmds.disconnectAttr(connected[0], joint + ".translate")
                    cmds.setAttr(
                        joint + ".translate", *cmds.getAttr("HipsRef_jnt.translate")[0]
                    )
        except:  # noqa E722
            pass

    print("# Pipeline : {} diconnected".format(character))
