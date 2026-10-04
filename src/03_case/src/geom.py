"""Small 2D/3D helpers shared by the part builders."""
from build123d import Pos, Rectangle, RectangleRounded, extrude

from params import PCB_X0, PCB_X1, PCB_Y0, PCB_Y1


def rect(x0, y0, x1, y1, r=0.0):
    w, h = x1 - x0, y1 - y0
    shape = RectangleRounded(w, h, r) if r > 0 else Rectangle(w, h)
    return Pos((x0 + x1) / 2, (y0 + y1) / 2) * shape


def pcb_offset(off, r):
    """The PCB outline grown by `off` with corner radius `r`."""
    return rect(PCB_X0 - off, PCB_Y0 - off, PCB_X1 + off, PCB_Y1 + off, r)


def outer_face():
    """Outside outline of the case: thinner walls left/right than front/back."""
    from params import OUTER_OFF, OUTER_SIDE, OUTER_R
    return rect(PCB_X0 - OUTER_SIDE, PCB_Y0 - OUTER_OFF, PCB_X1 + OUTER_SIDE, PCB_Y1 + OUTER_OFF, OUTER_R)


def prism(face, z0, z1):
    return Pos(0, 0, z0) * extrude(face, z1 - z0)


def edge_point(edge, pos, off):
    """Point `off` mm outside the PCB edge, at `pos` along it (x for back/front, y for sides)."""
    return {"back": (pos, PCB_Y1 + off), "front": (pos, PCB_Y0 - off),
            "left": (PCB_X0 - off, pos), "right": (PCB_X1 + off, pos)}[edge]


def edge_rect(edge, pos, width, inner, outer, r=0.0):
    """Rectangle straddling a PCB edge: `inner` mm inside to `outer` mm outside, `width` along it."""
    if edge in ("back", "front"):
        s = 1 if edge == "back" else -1
        y = PCB_Y1 if edge == "back" else PCB_Y0
        ya, yb = sorted((y - s * inner, y + s * outer))
        return rect(pos - width / 2, ya, pos + width / 2, yb, r)
    s = 1 if edge == "right" else -1
    x = PCB_X1 if edge == "right" else PCB_X0
    xa, xb = sorted((x - s * inner, x + s * outer))
    return rect(xa, pos - width / 2, xb, pos + width / 2, r)
