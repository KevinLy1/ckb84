"""Approximate Cherry-style PCB screw-in stabilizers (TX AP long pole), for fit checks.

TX publishes no CAD, so the housings use the Cherry screw-in envelope (TX follows it):
  - housing width 6.65 mm (Cherry spec; some CAD uses 6.75-6.8, checked as worst case)
  - the part that rises through the plate spans -5.53 .. +6.77 mm from the stem,
    towards the 3.99 mm (screw) hole
  - the base under the plate covers both PCB holes; a screw from below in the 3.99 mm hole
The wire is not modelled: its exact path is not published and it does not touch the plate cutout.
Keyboard frame (see params.py): PCB top = 0, plate 3.5 .. 5.0.
"""
import math

from build123d import Box, Compound, Cylinder, Pos, Rot

from params import PLATE_Z0, PLATE_Z1, PCB_T
import pcb_data

HOUSING_W = 6.65
HOUSING_W_MAX = 6.8                 # widest housing seen in community CAD
UPPER_V0, UPPER_V1 = -5.53, 6.77    # body through the plate, from the stem towards the screw hole
UPPER_TOP = PLATE_Z1 + 4.0          # housing top above the plate
BASE_V0, BASE_V1 = -8.6, 10.0       # base on the PCB, covering both holes
BASE_TOP = PLATE_Z0 - 0.3           # stays under the plate
BIG_V, SMALL_V = 8.255, -6.985      # PCB hole positions from the stem
STEM_U, STEM_V, STEM_TOP = 2.8, 4.2, PLATE_Z1 + 7.0
SCREW_HEAD_D, SCREW_HEAD_H = 4.6, 1.4
STAB_COLOR = (0.1, 0.1, 0.11)       # TX AP housings are black/smoke
CUTOUT_SHIFT = 1.52                 # plate cutout centre beyond the stem (see plate.py)


def _box(u0, u1, v0, v1, z0, z1):
    return Pos((u0 + u1) / 2, (v0 + v1) / 2, (z0 + z1) / 2) * Box(u1 - u0, v1 - v0, z1 - z0)


def housing(width=HOUSING_W):
    """One housing in its local frame: stem at the origin, +v towards the 3.99 mm screw hole."""
    w = width / 2
    parts = [
        _box(-w, w, UPPER_V0, UPPER_V1, 0, UPPER_TOP),          # body through the plate
        _box(-w, w, BASE_V0, BASE_V1, 0, BASE_TOP),             # base on the PCB
        Pos(0, BIG_V, -PCB_T / 2) * Cylinder(3.9 / 2, PCB_T),   # screw boss in the 3.99 hole
        Pos(0, SMALL_V, -PCB_T / 2) * Cylinder(2.95 / 2, PCB_T),  # peg in the 3.05 hole
        Pos(0, BIG_V, -PCB_T - SCREW_HEAD_H / 2) * Cylinder(SCREW_HEAD_D / 2, SCREW_HEAD_H),
        _box(-STEM_U / 2, STEM_U / 2, -STEM_V / 2, STEM_V / 2, UPPER_TOP, STEM_TOP),  # stem
    ]
    return parts


def placements():
    """(ref, side index, x, y, angle_deg) of every housing; angle turns local +v onto the screw hole."""
    _, stabs = pcb_data.read()
    out = []
    for st in stabs:
        for i, side in enumerate(st["sides"]):
            dx, dy = side["towards"]
            stem_x, stem_y = side["x"] - dx * CUTOUT_SHIFT, side["y"] - dy * CUTOUT_SHIFT
            out.append((st["ref"], i, stem_x, stem_y, math.degrees(math.atan2(-dx, dy))))
    return out


def stabilizers(width=HOUSING_W):
    solids = []
    for _, _, x, y, a in placements():
        for p in housing(width):
            solids.append(Pos(x, y, 0) * Rot(0, 0, a) * p)
    return Compound(solids)


def upper_bodies(width):
    """Only the parts that pass through the plate, per housing: for the cutout clearance check."""
    out = []
    w = width / 2
    for ref, i, x, y, a in placements():
        out.append((f"{ref}-{i}", Pos(x, y, 0) * Rot(0, 0, a) * _box(-w, w, UPPER_V0, UPPER_V1, 0, UPPER_TOP)))
    return out
