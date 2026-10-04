"""Build every part (monobloc 8 deg bottom case), run fit checks, export STEP / STL / DXF to ../out/."""
import sys
from pathlib import Path

from build123d import *

from params import *
import plate as plate_mod
import case
import hardware
import stabs as stabs_mod

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "out"
OUT.mkdir(exist_ok=True)


def load_pcb(full=True):
    s = import_step(ROOT / "in" / ("pcb_full.step" if full else "pcb.step"))
    return Pos(-KX0, KY0, -PCB_T) * s


def _overlap(b1, b2):
    return (b1.min.X < b2.max.X and b1.max.X > b2.min.X and b1.min.Y < b2.max.Y and
            b1.max.Y > b2.min.Y and b1.min.Z < b2.max.Z and b1.max.Z > b2.min.Z)


def interference(a, b):
    """Overlap volume between two shapes, solid by solid, skipping non-touching boxes."""
    total, hits = 0.0, []
    b_solids = [(s, s.bounding_box()) for s in b.solids()]
    for sa in a.solids():
        ba = sa.bounding_box()
        for sb, bb in b_solids:
            if not _overlap(ba, bb):
                continue
            common = sa & sb
            v = sum(s.volume for s in common.solids()) if common else 0.0
            if v > 1e-3:
                total += v
                hits.append((round(ba.center().X, 1), round(ba.center().Y, 1), round(ba.center().Z, 1), round(v, 3)))
    return round(total, 3), hits[:8]


def near_case(pcb):
    """Only PCB solids that can reach case material: above the top-case underside,
    below the floor, or outside the plate outline."""
    keep = []
    for s in pcb.solids():
        bb = s.bounding_box()
        if (bb.max.Z > TOP_LEDGE_Z - 0.01 or bb.min.Z < FLOOR_Z + 0.01 or bb.min.X < PCB_X0 or
                bb.max.X > PCB_X1 or bb.min.Y < PCB_Y0 or bb.max.Y > PCB_Y1):
            keep.append(s)
    return Compound(keep)


def monobloc_bumpons():
    """4 flat bumpons in the recesses of the angled underside."""
    n = case.desk_plane().z_dir
    return Compound([hardware.bumpon(case.foot_point(x, y) + n * FOOT_DEPTH, -n) for x, y in case.foot_positions()])


def usb_cable():
    """Standard USB-C plug (12.2 x 6.5 mm overmold) fully inserted, plus 40 mm of cable."""
    face_y = USB_MOUTH_Y + 0.45          # overmold face when the plug is fully mated
    axis = lambda y: Plane(origin=(USB_X, y, USB_Z), x_dir=(1, 0, 0), z_dir=(0, 1, 0))
    shell = extrude(axis(face_y - 6.65) * SlotOverall(8.34, 2.56), 6.65)
    overmold = extrude(axis(face_y) * SlotOverall(12.2, 6.5), 20)
    cable = extrude(axis(face_y + 20) * Circle(2.0), 40)
    return shell + overmold + cable


def main(checks=True):
    case.check_magnet_clearance()
    plate_face = plate_mod.plate_face()
    plate = plate_mod.plate()
    top = case.top_case()
    bottom = case.bottom_case()
    pcb = load_pcb(full=True)
    mag_bottom, mag_top = hardware.magnets()
    pads = hardware.gaskets()
    stabs = stabs_mod.stabilizers()

    if checks:
        print("== fit checks (volume of overlap, mm^3; expect 0) ==", flush=True)
        pcb_near = near_case(pcb)
        print(f"  {len(pcb.solids())} PCB solids, {len(pcb_near.solids())} near case material", flush=True)
        for name, a, b in [("plate/top", plate, top), ("plate/bottom", plate, bottom),
                           ("top/bottom", top, bottom), ("pcb+parts/bottom", pcb_near, bottom),
                           ("pcb+parts/top", pcb_near, top),
                           ("magnets/bottom", mag_bottom, bottom), ("magnets/top", mag_top, top),
                           ("magnets/other case", mag_bottom, top), ("gaskets/plate", pads, plate),
                           ("gaskets/top", pads, top), ("gaskets/bottom", pads, bottom),
                           ("gaskets/pcb+parts", pads, pcb_near),
                           ("stabs/plate", stabs, plate), ("stabs/top", stabs, top),
                           ("stabs/bottom", stabs, bottom),
                           ("case foam/pcb+parts", hardware.case_foam(),
                            Compound([s for s in pcb.solids() if s.bounding_box().min.Z < FLOOR_Z + hardware.CASE_FOAM_T])),
                           ("pcb foam/stabs", hardware.pcb_foam(), stabs)]:
            print(f"  {name:18} {interference(a, b)}", flush=True)
        plug = usb_cable()
        print(f"  {'usb plug/bottom':18} {interference(plug, bottom)}  "
              f"(overmold face {0.45 - USB_SLOT_STOP:.2f} mm clear of the slot end)", flush=True)

    # per-part exports, in the keyboard frame (machining frame)
    for name, part in [("plate", plate), ("top_case", top), ("bottom_case", bottom)]:
        export_step(part, OUT / f"{name}.step")
        export_stl(part, OUT / f"{name}.stl", tolerance=0.05, angular_tolerance=0.2)

    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_shape(plate_face)
    dxf.write(OUT / "plate.dxf")
    dxf = ExportDXF(unit=Unit.MM)
    dxf.add_shape(hardware.foam_face())
    dxf.write(OUT / "case_foam.dxf")

    # assembly on the desk
    parts = {"bottom_case": bottom, "plate": plate, "top_case": top, "pcb": pcb,
             "magnets_bottom": mag_bottom, "magnets_top": mag_top, "gaskets": pads, "stabs": stabs}
    world = {k: case.to_world(v) for k, v in parts.items()}
    colors = {"bottom_case": Color(0.64, 0.09, 0.11), "top_case": Color(0.77, 0.12, 0.14),
              "plate": Color(0.85, 0.7, 0.3), "pcb": Color(0.1, 0.4, 0.15),
              "magnets_bottom": Color(*hardware.MAG_COLOR), "magnets_top": Color(*hardware.MAG_COLOR),
              "gaskets": Color(*hardware.GASKET_COLOR),
              "stabs": Color(*stabs_mod.STAB_COLOR)}
    children = []
    for k, v in world.items():
        v.label, v.color = k, colors[k]
        children.append(v)
    asm = Compound(children=children, label="keyboard")
    export_step(asm, OUT / "assembly.step")

    # light meshes for the web viewer (board without components)
    web = OUT / "web"
    web.mkdir(exist_ok=True)
    board = load_pcb(full=False)
    world["pcb"] = case.to_world(board)
    for k, v in world.items():
        export_stl(v, web / f"{k}.stl", tolerance=0.1, angular_tolerance=0.3)
    # components only (everything in the full export that is not the bare board)
    bb = board.bounding_box()
    is_board = lambda s: abs(s.bounding_box().size.X - bb.size.X) < 1 and abs(s.bounding_box().size.Y - bb.size.Y) < 1
    # keycaps are the only tall solids at least one key wide (switch sockets and parts are smaller)
    is_cap = lambda s: (s.bounding_box().size.X > 17 or s.bounding_box().size.Y > 17) and s.bounding_box().size.Z > 5
    caps = [s for s in pcb.solids() if is_cap(s) and not is_board(s)]
    comps = [s for s in pcb.solids() if not is_board(s) and not is_cap(s)]
    print(f"  viewer: {len(caps)} keycaps, {len(comps)} other components")
    export_stl(case.to_world(Compound(comps)), web / "components.stl", tolerance=0.15, angular_tolerance=0.5)
    export_stl(case.to_world(Compound(caps)), web / "keycaps.stl", tolerance=0.15, angular_tolerance=0.5)
    export_stl(case.to_world(usb_cable()), web / "cable.stl", tolerance=0.05, angular_tolerance=0.2)
    for name, part in [("case_foam", hardware.case_foam()), ("pcb_foam", hardware.pcb_foam()),
                       ("bumpons", monobloc_bumpons())]:
        export_stl(case.to_world(part), web / f"{name}.stl", tolerance=0.1, angular_tolerance=0.3)
    return parts, world


if __name__ == "__main__":
    checks = "--no-checks" not in sys.argv
    main(checks=checks)
    print("exported to", OUT)
