"""In this pipeline :
    - an asset is written "prefix_assetName"
    - a task is a task to perform on an asset (eg: modeling, animation, rig...)
    - an assset task is written "prefix_assetName_suffix"
    - a scene is a working file writter "prefix_assetName_suffix_version_comment.ext"

    - every asset have :
        - tasks to do for the asset
        - a publish folder to export to unreal
        - rigged assets have a mPublish to export the geo as an fbx to maya

    - every task have:
        - a WIP folder (local, to work but not to share with the team)
        - a DEF folder (to share and save on git)

    - every publish have:
        - a fbx for the model and/or the animation
        - a texture folder
"""

# TODO :
#   - changer liste par tree widget pour avoir les taches

#   - save on github
#   - sanity check
#       - check published assets names
#       - check no files WIP without def
#   - in animation, make sur all references in layout are active
#   - publish textures
