"""Setup the package."""

import os

from python_core.types import items

VERSION = "2.0.0"
PATH = items.File(__file__).get_upstream(3)


def doc():
    """Open the autodoc documentation in a browser."""

    HTML = os.path.join(PATH, "docs", "build", "index.html")
    if os.path.exists(HTML):
        os.popen(HTML)
