"""Dimensioned technical drawings (SVG): plate, top case, bottom case and its section."""
import math
from pathlib import Path

from build123d import *

from params import *
import case
import plate as plate_mod

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs" / "drawings"
DOCS.mkdir(parents=True, exist_ok=True)

draft = Draft(font_size=3.0, decimal_precision=1, display_units=False, arrow_length=2.5,
              line_width=0.15, pad_around_text=1.0)
INK, DIM, THIN, CUT = (0.1, 0.1, 0.1), (0.05, 0.3, 0.7), (0.55, 0.55, 0.55), (0.75, 0.2, 0.2)


def sheet(name, layers, title, scale=2.4):
    exp = ExportSVG(scale=scale, margin=8, line_weight=0.25)
    for lname, color, shapes, fill in layers:
        exp.add_layer(lname, line_color=color, fill_color=fill, line_weight=0.25 if lname != "dims" else 0.12)
        for s in shapes:
            exp.add_shape(s, layer=lname)
    exp.add_layer("title", line_color=INK, fill_color=INK)
    bb = Compound([s for _, _, ss, _ in layers for s in ss]).bounding_box()
    exp.add_shape(Pos(bb.min.X, bb.min.Y - 14) * Text(title, 5, align=(Align.MIN, Align.MIN)), layer="title")
    exp.write(DOCS / f"{name}.svg")
    print("wrote", name)


def section_edges(shape, z):
    return shape.intersect(Pos(0, 0, z) * Box(1000, 1000, 1e-3)).edges() if shape else []


def outline(shape, z):
    """Plan-view outline of `shape` at height z (keyboard frame)."""
    return Compound(section(shape, Plane.XY.offset(z)).edges())


def _dim(p0, p1, off, label):
    if off == 0:
        return DimensionLine([p0, p1], draft=draft, label=label)
    return ExtensionLine([p0, p1], offset=off, draft=draft, label=label)


def hdim(x0, x1, y, off, label=None):
    return _dim((x0, y), (x1, y), off, label)


def vdim(y0, y1, x, off, label=None):
    return _dim((x, y0), (x, y1), off, label)


def note(x, y, text, size=3.0):
    return Pos(x, y) * Text(text, size, align=(Align.MIN, Align.CENTER))


# ---------------------------------------------------------------------------------

def plate_sheet():
    face = plate_mod.plate_face()
    _, _, tabs = plate_mod.layout()
    dims = [hdim(PCB_X0, PCB_X1, PCB_Y0, -16), vdim(PCB_Y0, PCB_Y1, PCB_X1, -18),
            hdim(PCB_X0 - TAB_P, PCB_X1 + TAB_P, PCB_Y0, -26),
            vdim(PCB_Y0 - TAB_P, PCB_Y1 + TAB_P, PCB_X1, -30)]
    t = tabs[0]
    dims += [hdim(t["a"], t["b"], PCB_Y1 + TAB_P, 8), vdim(PCB_Y1, PCB_Y1 + TAB_P, t["b"], -8)]
    notes = [note(PCB_X0, PCB_Y1 + 30, "PLATE  -  1.5 mm FR4 or polycarbonate  -  laser / CNC from plate.dxf"),
             note(PCB_X0, PCB_Y1 + 24, "84x MX cutout 14.0 x 14.0 (R0.5)   10x stab cutout 7.0 x 15.0 (R0.5)"),
             note(PCB_X0, PCB_Y1 + 18, f"{len(tabs)} gasket tabs, protrusion {TAB_P:.1f}, flex slots {RELIEF_W} wide x 6-7 deep"),
             note(PCB_X0, PCB_Y1 + 12, "Stab cutouts follow the PCB footprints (4 of 5 are flipped vs. ai03 plate)")]
    sheet("01_plate", [("part", INK, face.edges(), None), ("dims", DIM, dims, DIM),
                       ("notes", INK, notes, INK)], "Sheet 1 - Plate (top view, keyboard frame)")


def top_case_sheet():
    top = case.top_case()
    o, s = OUTER_OFF, OUTER_SIDE
    lines = list(outline(top, TOP_Z - 2).edges())
    hidden = list(outline(top, SPLIT_Z + 0.5).edges())
    key_y0 = -6.25 * U
    dims = [hdim(-s, PCB_X1 + s, PCB_Y0 - o, -14), vdim(PCB_Y0 - o, PCB_Y1 + o, PCB_X1 + s, -14),
            hdim(-OPENING_OFF, PCB_X1 + OPENING_OFF, key_y0 - OPENING_OFF, 8),
            vdim(key_y0 - OPENING_OFF, OPENING_OFF, PCB_X1 + OPENING_OFF, -8),
            vdim(OPENING_OFF, PCB_Y1 + o, 40, 0),
            hdim(-s, -OPENING_OFF, -60, 0),
            vdim(BRIDGE_Y0, BRIDGE_Y1, 160, 0)]
    notes = [note(-s, PCB_Y1 + o + 26, f"TOP CASE  -  ABS  -  thickness {TOP_Z - SPLIT_Z:.1f}  -  outer corners R{OUTER_R:.0f}, top edge fillet R{TOP_EDGE_FILLET}"),
             note(-s, PCB_Y1 + o + 20, f"Underside recess {TOP_LEDGE_Z - SPLIT_Z:.1f} deep (presses top gaskets)   opening corners R{OPENING_R} (2 mm end mill)"),
             note(-s, PCB_Y1 + o + 14, f"F-row bridge {BRIDGE_Y1 - BRIDGE_Y0:.2f} wide hides the 0.25U gap   {len(MAGNETS)}x magnet pocket D{MAG_POCKET_D} x {MAG_POCKET_H} (underside)"),
             note(165, (BRIDGE_Y0 + BRIDGE_Y1) / 2, "bridge")]
    sheet("02_top_case", [("hidden", THIN, hidden, None), ("part", INK, lines, None),
                          ("dims", DIM, dims, DIM), ("notes", INK, notes, INK)],
          "Sheet 2 - Top case (top view; grey = underside recess, tab & magnet pockets)")


def bottom_case_sheet():
    bot = case.bottom_case()
    lines = list(outline(bot, SPLIT_Z - 0.5).edges()) + list(outline(bot, SPLIT_Z + 0.5).edges())
    deep = list(outline(bot, FLOOR_Z + 0.5).edges())
    o, s = OUTER_OFF, OUTER_SIDE
    dims = [hdim(-s, PCB_X1 + s, PCB_Y0 - o, -14), vdim(PCB_Y0 - o, PCB_Y1 + o, PCB_X1 + s, -14),
            hdim(-CAV_GAP, PCB_X1 + CAV_GAP, PCB_Y0 - CAV_GAP, 6),
            vdim(PCB_Y0 - CAV_GAP, PCB_Y1 + CAV_GAP, PCB_X1 + CAV_GAP, -6),
            hdim(USB_X - USB_SLOT_W / 2, USB_X + USB_SLOT_W / 2, PCB_Y1 + o, 6)]
    notes = [note(-s, PCB_Y1 + o + 38, "BOTTOM CASE  -  ABS  -  setup 1: top (cavity, lip, pockets)  -  setup 2: underside at 8 deg  -  setup 3: back face (USB slot)"),
             note(-s, PCB_Y1 + o + 44, f"USB-C slot: stadium {USB_SLOT_W} x {USB_SLOT_H} through back wall, centre {SPLIT_Z - USB_Z:.2f} below parting face, x = {USB_X:.2f} from key-area left edge"),
             note(-s, PCB_Y1 + o + 26, f"Cavity floor {SPLIT_Z - FLOOR_Z:.2f} below parting face; alignment lip {LIP_H} high x {LIP_OFF1 - LIP_OFF0} wide"),
             note(-s, PCB_Y1 + o + 20, f"Tab ledges {SPLIT_Z - BOT_LEDGE_Z:.1f} below parting face   {len(MAGNETS)}x magnet pocket D{MAG_POCKET_D} x {MAG_POCKET_H}"),
             note(-s, PCB_Y1 + o + 14, f"Underside: 4x foot recess D{FOOT_D} x {FOOT_DEPTH}"),
             note(USB_X - 6, PCB_Y1 + o + 3, "USB-C")]
    sheet("03_bottom_case", [("deep", THIN, deep, None), ("part", INK, lines, None),
                             ("dims", DIM, dims, DIM), ("notes", INK, notes, INK)],
          "Sheet 3 - Bottom case (top view; grey = cavity floor and feet)")


def section_sheet(name="04_section"):
    """Section A-A in the desk frame, drawn as (y, z), at x = 100."""
    x = 100.0
    src = {"top": case.top_case(), "bottom": case.bottom_case(), "plate": plate_mod.plate()}
    parts = {k: case.to_world(v) for k, v in src.items()}
    pl = Plane(origin=(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
    layers = []
    for k, color in [("bottom", INK), ("top", INK), ("plate", CUT)]:
        sec = section(parts[k], pl)
        layers.append((k, color, [pl.to_local_coords(f) for f in sec.faces()], (0.85, 0.85, 0.85) if k != "plate" else CUT))
    allb = Compound([s for _, _, ss, _ in layers for s in ss]).bounding_box()
    y0, y1, ztop_f, ztop_b = allb.min.X, allb.max.X, None, allb.max.Y
    front_h = case.to_world(Pos(0, PCB_Y0 - OUTER_OFF, TOP_Z)).position
    back_h = case.to_world(Pos(0, PCB_Y1 + OUTER_OFF, TOP_Z)).position
    plate_home = case.to_world(Pos(0, -3.75 * U, PLATE_Z1)).position
    dims = [hdim(y0, y1, 0, 10),
            vdim(0, front_h.Z, front_h.Y, -8),
            vdim(0, back_h.Z, back_h.Y, 8),
            vdim(0, plate_home.Z, plate_home.Y, 0)]
    # 8 deg reference
    ang = [Polyline((front_h.Y, front_h.Z + 12), (back_h.Y + 10, front_h.Z + 12)),
           Polyline((front_h.Y, front_h.Z + 12),
                    (front_h.Y + 160 * math.cos(TILT), front_h.Z + 12 + 160 * math.sin(TILT)))]
    notes = [note(front_h.Y + 60, front_h.Z + 22, f"{TILT_DEG:.0f} deg typing angle (built into the case)"),
             note(plate_home.Y + 2, plate_home.Z * 0.75, "plate top at home row"),
             note(y0, allb.max.Y + 40, "Stack (keyboard frame, PCB top = 0):"),
             note(y0, allb.max.Y + 34, f"PCB -{PCB_T} .. 0   plate {PLATE_Z0} .. {PLATE_Z1}   gaskets {GASKET_T} -> {GASKET_GAP:.1f} (20 %)"),
             note(y0, allb.max.Y + 28, f"top case {SPLIT_Z} .. {TOP_Z} (recess to {TOP_LEDGE_Z:.1f})   bottom ledge {BOT_LEDGE_Z:.1f}   floor {FLOOR_Z:.2f}")]
    layers += [("dims", DIM, dims + ang, DIM), ("notes", INK, notes, INK)]
    sheet(name, layers, f"Sheet {name[:2].lstrip('0')} - Section A-A at x = {x:.1f} (side view, desk frame; red = plate)",
          scale=3.0)


if __name__ == "__main__":
    plate_sheet()
    top_case_sheet()
    bottom_case_sheet()
    section_sheet()
