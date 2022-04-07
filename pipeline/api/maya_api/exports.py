"""Manage scene exportations."""

import os
import shutil

from python_core.types import strings

from pipeline.api.maya_api import maya_asset, creation, studient_warning
from pipeline.api.maya_api.tools import rig, animation
from pipeline.utils import database

ASSET = maya_asset.MayaAsset()
DATABASE = database.Database()


def save_def():
    """Save the DEF version of the asset to publish it on git."""

    from maya import cmds

    app_data = DATABASE.app_data

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the pipe node of the current task to check if we're in a bake scene
    pipe_node = app_data["tasks"][task]["pipe_node"]
    if task == "animation" and cmds.getAttr(pipe_node + ".BakeScene"):
        print(
            "# Pipeline : DEF file not created ->"
            + " you can't save a bake file as DEF."
        )
        return

    # deduce the destination path
    source = cmds.file(q=True, sceneName=True)
    destination = ASSET.get_path_from_name(os.path.basename(source), def_path=True)

    # make sure the DEF directory exists
    ASSET.create_directories(destination)

    # remove the previous maya files in the current directory
    for root, dirs, def_files in os.walk(destination):
        for file in def_files:
            if file.startswith(asset_name) and file.endswith(".ma"):
                os.remove(os.path.join(root, file))

    # set the destination file path
    destination = os.path.join(destination, os.path.basename(source))

    # copy the file to the DEF path
    shutil.copy2(source, destination)

    # clean studient warning
    studient_warning.remove_from_file(destination)

    print("# Pipeline : DEF saved -> " + destination)


# publish form Maya


def export():
    """Export the scene to be able to load it in an other maya scene or else."""

    # get the tasks informations
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations

    # export differently depending on the current task
    if task == "modeling":
        if asset_type != "atlas":
            _export_modeling()

    elif task == "rig":
        _export_rig()

    elif task == "layout":
        _export_layout()

    elif task == "cleaning":
        _export_cleaning()

    elif task == "animation":
        print("# Pipeline : You don't need to export the animation task from maya")


def _export_modeling():
    """Export the GEO group as fbx in an export folder."""

    from maya import cmds, mel

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the path to save the publish in
    path = os.path.join(ASSET.get_path_from_name(asset_name), task, "export")
    ASSET.create_directories(path)

    # uncheck the include children and input connection check boxes
    if mel.eval("FBXExportIncludeChildren  -q"):
        mel.eval("FBXExportIncludeChildren  -v false")
    if mel.eval("FBXExportInputConnections -q"):
        mel.eval("FBXExportInputConnections -v false")

    # publish the GEO group
    cmds.select(cmds.listRelatives("GEO", allDescendents=True, type="mesh"))
    path = os.path.join(path, asset_name + ".fbx")
    cmds.file(
        path,
        force=True,
        options="v=0;",
        type="FBX export",
        preserveReferences=True,
        exportSelected=True,
    )

    print("# Pipeline : Modeling exported -> " + path)


def _export_rig():
    """Save the current file in an export folder to be imported as reference."""

    print("# Pipeline : Rig exported -> " + _copy_export_current_scene())


def _export_layout():
    """Save the current file in an export folder to be imported as reference."""

    print("# Pipeline : Layout exported -> " + _copy_export_current_scene())


def _export_cleaning():
    """Save the current file in an export folder to be imported as reference."""

    print("# Pipeline : Cleaning exported -> " + _copy_export_current_scene())


def _copy_export_current_scene():
    """Copy the current scene and name it properly in the export folder.

    It will allow to import it as a reference later one in the project.

    :return: The created export file path
    :rtype: str
    """

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, asset_comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # deduce the source and destination path
    source = os.path.join(cmds.file(q=True, sceneName=True))
    destination = os.path.join(ASSET.get_path_from_name(asset_name), task, "export")

    # make sure the path exists
    ASSET.create_directories(destination)

    # set the destination file path
    destination = os.path.join(destination, asset_name + ".ma")

    # copy the file to the export path
    shutil.copy2(source, destination)

    # clean studient warning
    studient_warning.remove_from_file(destination)

    return destination


# publish for Unreal


def publish():
    """Publish to unreal."""

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations

    # export differently depending on the current task
    if task == "modeling":
        if asset_type == "atlas":
            _publish_atlas()
        else:
            _publish_modeling()

    elif task == "rig":
        _publish_rig()

    elif task == "layout":
        _publish_layout()

    elif task == "animation":
        publish_animation()


def _publish_modeling():
    """Export the GEO group as fbx in the unreal publish folder."""

    from maya import cmds, mel

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the path to save the publish in
    path = os.path.join(ASSET.get_path_from_name(asset_name), "publish")
    ASSET.create_directories(path)

    # only the include children check box
    if not mel.eval("FBXExportIncludeChildren  -q"):
        mel.eval("FBXExportIncludeChildren  -v true")
    if mel.eval("FBXExportInputConnections -q"):
        mel.eval("FBXExportInputConnections -v false")

    # publish only meshes in GEO group
    cmds.select(cmds.listRelatives("GEO", allDescendents=True, type="mesh"))
    path = os.path.join(path, asset_name + ".fbx")
    cmds.file(
        path,
        force=True,
        options="v=0;",
        type="FBX export",
        preserveReferences=True,
        exportSelected=True,
    )

    print("# Pipeline : Modeling published -> " + path)


def _publish_atlas():
    """Export the all the geos in GEO group as obj in the unreal publish folder."""

    from maya import cmds

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the path to save the publish in
    path = os.path.join(ASSET.get_path_from_name(asset_name), "publish")
    ASSET.create_directories(path)

    # publish only meshes in GEO group
    meshes = cmds.listRelatives("GEO", allDescendents=True, type="mesh")
    meshes = [cmds.listRelatives(mesh, parent=True)[0] for mesh in meshes]

    done = list()
    for mesh in meshes:
        if mesh in done:
            continue

        cmds.select(mesh)

        export_path = os.path.join(
            path, "_".join(["at", strings.camel_case(mesh, lower_first=True) + ".obj"])
        )

        cmds.file(
            export_path,
            force=True,
            options="groups=1;ptgroups=1;materials=1;smoothing=1;normals=1",
            type="OBJexport",
            preserveReferences=True,
            exportSelected=True,
        )

        done.append(mesh)

        print("# Pipeline : Atlas published -> " + export_path)

    print("# Pipeline : {} meshes exported".format(len(done)))


def _publish_rig():
    """Export the GEO and RIG groups as fbx in the unreal publish folder."""

    from maya import cmds, mel

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the path to save the publish in
    path = os.path.join(ASSET.get_path_from_name(asset_name), "publish")
    ASSET.create_directories(path)
    path = os.path.join(path, asset_name + ".fbx")

    # get if we export a blendshape
    rig.select_joints_to_export()
    blendshape = False
    for node in cmds.ls(sl=True):
        for history in cmds.listHistory(node):
            if cmds.objectType(history, isType="blendShape"):
                blendshape = True
                print("# Pipeline : Blendshape found")
                break

    # uncheck the include children and input connection check boxes
    if mel.eval("FBXExportIncludeChildren  -q"):
        mel.eval("FBXExportIncludeChildren  -v false")
    if mel.eval("FBXExportInputConnections -q"):
        mel.eval(
            "FBXExportInputConnections -v {}".format("true" if blendshape else "false")
        )

    # publish the GEO group and the joints in the pipe node
    rig.select_joints_to_export()
    cmds.select(cmds.listRelatives("GEO", allDescendents=True, type="mesh"), add=True)
    cmds.file(
        path,
        force=True,
        options="v=0;",
        type="FBX export",
        preserveReferences=True,
        exportSelected=True,
    )

    print("# Pipeline : Rig published -> " + path)


def _publish_layout():
    """Export the LAYOUT group as fbx in the unreal publish folder."""

    from maya import cmds, mel

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the path to save the publish in
    path = os.path.join(ASSET.get_path_from_name(asset_name), "publish")
    ASSET.create_directories(path)

    # check the include children and input connection check boxes
    if not mel.eval("FBXExportIncludeChildren  -q"):
        mel.eval("FBXExportIncludeChildren  -v true")
    if not mel.eval("FBXExportInputConnections -q"):
        mel.eval("FBXExportInputConnections -v true")

    # publish the GEO group and the PIPE_NODE
    cmds.select("LAYOUT")
    path = os.path.join(path, asset_name + "_layout.fbx")
    cmds.file(
        path,
        force=True,
        options="v=0;",
        type="FBX export",
        preserveReferences=True,
        exportSelected=True,
    )

    print("# Pipeline : Layout published -> " + path)


def _publish_mocap():
    """Do nothing."""


def publish_animation(pipe_nodes=None):
    """Export the animations as fbx in the unreal publish folder.

    :param pipe_nodes: A list of pipe_nodes to get the joints to export from.
        If none, export all.
    :type pipe_nodes: list, none
    """

    from maya import cmds, mel

    # get informations on the current file
    informations = ASSET.get_informations_from_current_file()
    asset_type, basename, task, version, comment, path = informations
    asset_name = ASSET.get_asset_name(asset_type, basename)

    # get the path to save the publish in and create it if it doesn't exists
    publish_path = os.path.join(ASSET.get_path_from_name(asset_name), "publish")
    ASSET.create_directories(publish_path)

    # create the bake file and bake the assets to export ( = animateds)
    creation.create_bake_file()
    animateds = animation.bake_animations(pipe_nodes)

    # uncheck the include children and input connection check boxes
    if mel.eval("FBXExportIncludeChildren  -q"):
        mel.eval("FBXExportIncludeChildren  -v false")
    if mel.eval("FBXExportInputConnections -q"):
        mel.eval("FBXExportInputConnections -v true")

    # export the animations
    for asset_namespace, infos in animateds.items():
        # figure out the publish file name
        path = os.path.join(
            publish_path,
            "_".join([asset_namespace, asset_name.split("_")[1], "anim.fbx"]),
        )

        # TODO : delete these two lines (specific to welcome aboard) from the pipe
        # # disconnect the joints to export from their influence
        cmds.select(asset_namespace + ":RIG")
        animation.disconnect_rig_from_mocap()

        # publish the animated joints to publish
        rig.select_joints_to_export(asset_namespace + ":RIG")
        blendshape = False
        for node in cmds.ls(sl=True):
            for history in cmds.listHistory(node):
                if cmds.objectType(history, isType="blendShape"):
                    blendshape = True
                    print(
                        "# Pipeline : Blendshape found for {}".format(asset_namespace)
                    )
                    break
        if blendshape:
            # if we export a blendshape, only publish the meshes in GEO group
            rig.select_joints_to_export(asset_namespace + ":RIG")
            cmds.select(
                cmds.listRelatives(
                    asset_namespace + ":GEO", allDescendents=True, type="mesh"
                ),
                add=True,
            )
        else:
            rig.select_joints_to_export(asset_namespace + ":RIG")

        cmds.file(
            path,
            force=True,
            options="v=0;",
            type="FBX export",
            preserveReferences=True,
            exportSelected=True,
        )

        print("# Pipeline : Animation published -> " + path)
