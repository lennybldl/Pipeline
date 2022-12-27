"""Adjust the svgs view box to be a square."""

from python_core.types import items

images_path = items.File(__file__).get_upstream(2)
for _file in images_path.files():
    if _file.endswith(".svg"):
        content = _file.read()

        # get the current view box value
        view_box_values = content.split('viewBox="')[1]
        view_box_values = view_box_values.split('">')[0]

        # edit the view box
        content = content.replace(view_box_values, "-48 -48 96 96")
        _file.write(content)
