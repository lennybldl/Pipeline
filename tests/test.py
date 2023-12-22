import sys

from lbx_python_core import items

sys.path.insert(0, items.File(__file__).get_upstream(2) + "/src")

from lbx_pipeline import commands  # noqa E402

commands.start("windows")
commands.load(items.File(__file__).directory)
