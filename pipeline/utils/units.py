"""Manage units."""

import math


def convert_byte(byte):
    """Convert byte units to mega/giga/peta/...-octets.

    :param byte: The size in bytes
    :type bytes: int

    :return: The converted size and unit
    :rtype: tuple
    """

    if byte == 0:
        return 0, "B"

    unit = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]

    unit_power = int(math.floor(math.log(byte, 1024)))
    power = math.pow(1024, unit_power)
    size = round(byte / power, 2)

    return size, unit[unit_power]
