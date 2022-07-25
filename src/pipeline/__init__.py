"""Setup the package."""

import os


VERSION = "2.0.0"
PATH = os.path.abspath(os.path.join(__file__, *[".."] * 3))


def doc():
    """Open the autodoc documentation in a browser."""

    HTML = os.path.join(PATH, "docs", "build", "index.html")
    if os.path.exists(HTML):
        os.popen(HTML)
