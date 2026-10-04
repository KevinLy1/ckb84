"""Gasket-mount switch plate (1.5 mm FR4 or polycarbonate)."""
from functools import cache

from build123d import Pos, RectangleRounded

from params import *
from geom import pcb_offset, prism, edge_rect
import pcb_data


def cutout_boxes(switches, stabs):
    """Axis-aligned (x0, y0, x1, y1) boxes of every cutout."""
    boxes = []
    for s in switches:
        h = SW_CUT / 2
        boxes.append((s["x"] - h, s["y"] - h, s["x"] + h, s["y"] + h))
    for st in stabs:
        for d in st["sides"]:
            w, l = STAB_CUT_W / 2, STAB_CUT_L / 2
            hx, hy = (w, l) if d["axis_y"] else (l, w)
            boxes.append((d["x"] - hx, d["y"] - hy, d["x"] + hx, d["y"] + hy))
    return boxes


def _slot_clear(edge, p, depth, boxes):
    bb = edge_rect(edge, p, RELIEF_W, depth, 1.0).bounding_box()
    x0, y0, x1, y1 = bb.min.X, bb.min.Y, bb.max.X, bb.max.Y
    c = RELIEF_CLEAR
    return not any(x0 < b[2] + c and x1 > b[0] - c and y0 < b[3] + c and y1 > b[1] - c for b in boxes)


def _find_slot(edge, nominal, boxes):
    """Closest slot position to `nominal` that reaches the deepest depth available."""
    steps = sorted((i * 0.25 for i in range(-int(RELIEF_SEARCH * 4), int(RELIEF_SEARCH * 4) + 1)), key=abs)
    depth = RELIEF_MAX
    while depth >= RELIEF_MIN:
        for d in steps:
            if _slot_clear(edge, nominal + d, depth, boxes):
                return nominal + d, depth
        depth -= 0.5
    return None


@cache
def layout():
    """Switches, stabs, and the resolved tabs: list of dict(edge, a, b, slots)."""
    switches, stabs = pcb_data.read()
    boxes = cutout_boxes(switches, stabs)
    tabs = []
    for edge, c in TABS:
        ends, slots = [], []
        for side in (-1, 1):
            hit = _find_slot(edge, c + side * (TAB_W + RELIEF_W) / 2, boxes)
            if hit:
                p, depth = hit
                slots.append((p, depth))
                ends.append(p - side * RELIEF_W / 2)
            else:
                ends.append(c + side * TAB_W / 2)
        tabs.append(dict(edge=edge, a=ends[0], b=ends[1], slots=slots))
    return switches, stabs, tabs


def plate_face():
    switches, stabs, tabs = layout()
    face = pcb_offset(0, PLATE_CORNER_R)
    for t in tabs:
        face += edge_rect(t["edge"], (t["a"] + t["b"]) / 2, t["b"] - t["a"], TAB_P, TAB_P, TAB_R)
    for s in switches:
        face -= Pos(s["x"], s["y"]) * RectangleRounded(SW_CUT, SW_CUT, SW_CUT_R)
    for st in stabs:
        for d in st["sides"]:
            w, l = (STAB_CUT_W, STAB_CUT_L) if d["axis_y"] else (STAB_CUT_L, STAB_CUT_W)
            face -= Pos(d["x"], d["y"]) * RectangleRounded(w, l, SW_CUT_R)
    for t in tabs:
        for p, depth in t["slots"]:
            face -= edge_rect(t["edge"], p, RELIEF_W, depth, 1.0, RELIEF_W / 2 - 0.01)
    return face


def plate():
    return prism(plate_face(), PLATE_Z0, PLATE_Z1)


if __name__ == "__main__":
    _, _, tabs = layout()
    for t in tabs:
        print(f'{t["edge"]:5} {t["a"]:8.2f} .. {t["b"]:8.2f}  w={t["b"] - t["a"]:5.2f}  slots={t["slots"]}')
    face = plate_face()
    print("area", round(face.area), "faces", len(face.faces()))
