"""Manage common methods in maya."""

import os

from pipeline.api.assets import assets


class MayaAsset(assets.Assets):
    """Manage common methods for every maya asset."""

    def get_informations_from_current_file(self):
        """Figure out the asset information from the full file name.

        :return: A tuple of asset_type, basename, task, version, comment, path
        :rtype: tuple
        """

        from maya import cmds

        name = os.path.basename(cmds.file(q=True, sceneName=True))

        return self.get_informations_from_name(name)
