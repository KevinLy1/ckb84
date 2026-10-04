"""Bought-in parts placed in the assembly: magnets, gasket pads, foams, rubber feet (keyboard frame)."""
from build123d import Align, Box, Circle, Compound, Cylinder, Plane, Pos, RectangleRounded, Sphere

from params import *
from geom import prism, edge_rect, edge_point, pcb_offset, rect
from plate import layout
import pcb_data
import stabs as stabs_mod

GASKET_PAD_L = 15.0                 # along the plate edge
GASKET_PAD_W = 3.0                  # across: from the tab tip inwards
MAG_COLOR = (0.78, 0.79, 0.82)
GASKET_COLOR = (0.18, 0.22, 0.30)
FOAM_COLOR = (0.85, 0.83, 0.78)
FEET_COLOR = (0.08, 0.08, 0.09)
CASE_FOAM_T = 3.0
BUMPON_H = 3.0


def magnets():
    """(bottom, top) magnet sets, each flush with the parting face in its pocket."""
    bottom, top = [], []
    for e, p in MAGNETS:
        disc = Pos(*edge_point(e, p, MAG_OFF)) * Circle(MAG_D / 2)
        bottom.append(prism(disc, SPLIT_Z - MAG_H, SPLIT_Z))
        top.append(prism(disc, SPLIT_Z, SPLIT_Z + MAG_H))
    return Compound(bottom), Compound(top)


def gaskets():
    """Poron pads above and below every tab, compressed to GASKET_GAP, flush with the tab tip."""
    pads = []
    for t in layout()[2]:
        c = (t["a"] + t["b"]) / 2
        # edge_rect(inner, outer) measures from the PCB edge: pad spans TAB_P - W .. TAB_P outside
        face = edge_rect(t["edge"], c, GASKET_PAD_L, -(TAB_P - GASKET_PAD_W), TAB_P)
        pads.append(prism(face, BOT_LEDGE_Z, PLATE_Z0))
        pads.append(prism(face, PLATE_Z1, TOP_LEDGE_Z))
    return Compound(pads)


def foam_face():
    """Case foam: cavity minus clearance, with holes for the tall bottom-side parts."""
    face = pcb_offset(CAV_GAP - 0.5, CAV_R - 0.5)
    for ref, w, h in [("J1", 11.0, 9.0), ("C1", 9.0, 5.5), ("J2", 10.0, 4.0)]:
        x, y = pcb_data.kicad_part(ref)
        face -= rect(x - w / 2, y - h / 2, x + w / 2, y + h / 2)
    for kx, ky in RESETS:
        x, y = from_kicad(kx, ky)
        face -= Pos(x, y) * Circle(3.0)
    return face


def case_foam():
    """3 mm case foam lying on the cavity floor (same cavity in both bottom versions)."""
    return prism(foam_face(), FLOOR_Z, FLOOR_Z + CASE_FOAM_T)


def pcb_foam():
    """Optional PCB/plate foam: fills PCB top .. plate bottom, with switch and stabilizer holes.
    Every component except switches and stabilizers is on the PCB bottom side."""
    switches, _, _ = layout()
    face = pcb_offset(0, PLATE_CORNER_R)
    for s in switches:
        face -= Pos(s["x"], s["y"]) * RectangleRounded(SW_CUT, SW_CUT, SW_CUT_R)
    for st in stabs_mod.stabilizers().solids():
        bb = st.bounding_box()
        face -= rect(bb.min.X - 0.5, bb.min.Y - 0.5, bb.max.X + 0.5, bb.max.Y + 0.5)
    return prism(face, 0, PLATE_Z0)


def bumpon(origin, down):
    """10 x 3 mm flat rubber bumpon whose top face sits at `origin` (the recess floor); `down` points
    out of the part."""
    return Plane(origin=origin, z_dir=down) * Cylinder(FOOT_D / 2 - 0.2, BUMPON_H, align=(Align.CENTER, Align.CENTER, Align.MIN))
