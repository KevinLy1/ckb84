"""Hidden-line SVG views of the parts and the assembly (for review and the drawings)."""
from pathlib import Path

from build123d import *

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
VIEWS = ROOT / "out" / "views"
VIEWS.mkdir(parents=True, exist_ok=True)


def view(shape, name, origin, up=(0, 0, 1), hidden=False, line=0.25):
    visible, hid = shape.project_to_viewport(origin, viewport_up=up)
    size = max(*Compound(children=visible).bounding_box().size)
    exp = ExportSVG(scale=600 / size, margin=5, line_weight=line)
    exp.add_layer("visible", line_color=(30, 30, 30))
    exp.add_shape(visible, layer="visible")
    if hidden:
        exp.add_layer("hidden", line_color=(170, 170, 170), line_type=LineType.ISO_DOT)
        exp.add_shape(hid, layer="hidden")
    exp.write(VIEWS / f"{name}.svg")


if __name__ == "__main__":
    import sys
    names = sys.argv[1:] or ["top_case", "bottom_case", "plate"]
    for n in names:
        s = import_step(OUT / f"{n}.step")
        c = s.bounding_box().center()
        view(s, f"{n}_iso", (c.X - 250, c.Y - 400, c.Z + 300))
        view(s, f"{n}_top", (c.X, c.Y, c.Z + 1000), up=(0, 1, 0))
        view(s, f"{n}_bottom_iso", (c.X - 250, c.Y + 400, c.Z - 300))
        print("rendered", n)
