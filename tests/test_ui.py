import sys

sys.path.insert(0, r"C:\Users\Lenny\Documents\CODE_MesProjets\dev\0000_python_core\src")
from python_core.types import items
from python_core.pyside2.internal import database

database.set("tooltips_mode", 0)

sys.path.insert(0, items.File(__file__).get_upstream(2) + "/src")

from pipeline import ui  # noqa E402

path = items.Folder(
    r"C:\Users\Lenny\Documents\CODE_MesProjets\dev\0020_Pipeline\tests\testProject"
)
ui.launch_windows_ui()
