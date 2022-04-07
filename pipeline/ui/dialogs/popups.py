"""Create popups dialogs."""

import os

from pipeline.ui.dialogs import dialogs


def confirm(message="Confirm?"):
    """Build a dialog popup to ask confirmation or not.

    :param message: The message to ask when the dialog pops up.
    :type message: str
    """

    dialog = dialogs.YesNoDialog()

    # set the elements to display in the dialog
    dialog.title = "Confirm?"
    dialog.msg = message

    return dialog.exec_()


def save_popup():
    """Build a dialog popup to ask if we want to save the current file."""

    from maya import cmds

    # save before opening the new scene
    if cmds.file(q=True, modified=True):
        dialog = dialogs.YesNoDialog()

        # set the elements to display in the dialog
        dialog.title = "Save?"
        dialog.title_msg = os.path.basename(cmds.file(q=True, sceneName=True))
        dialog.msg = "Save changes to the current scene?"

        if dialog.exec_():
            file = cmds.file(q=True, sceneName=True).replace("/", "\\")
            if not file:
                raise ValueError(
                    "# Pipeline : This file has no name."
                    + " You have to save it at least once before."
                )

            print("# Pipeline : File saved -> " + file)
            cmds.file(save=True, type="mayaAscii", force=True)
