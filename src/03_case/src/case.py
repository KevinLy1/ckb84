"""Top and bottom case (CNC ABS), built in the keyboard frame (see params.py).

Every pocket is parallel to the plate, so both parts machine on a 3-axis mill.
The only angled face is the bottom-case underside (one flat face, cut at 8 deg).
"""
import math

from build123d import *

from params import *
from geom import rect, pcb_offset, prism, edge_point, edge_rect, outer_face
from plate import layout
import pcb_data

KEY_Y0 = -6.25 * U   # front edge of the key area (row 5 bottom)


# ---- shared features -----------------------------------------------------------

def tab_pockets(z0, z1):
    """Clearance pockets for the plate tabs + gaskets, from z0 to z1."""
    out = []
    for t in layout()[2]:
        c, w = (t["a"] + t["b"]) / 2, t["b"] - t["a"] + 2 * TAB_POCKET_CLEAR
        face = edge_rect(t["edge"], c, w, CAV_GAP + 1.0, TAB_P + TAB_POCKET_CLEAR, CAV_R)
        out.append(prism(face, z0, z1))
    return out


def magnet_pockets(z_face, direction):
    """Magnet pockets drilled into a face at z_face; direction -1 = down, +1 = up."""
    z0, z1 = sorted((z_face, z_face + direction * MAG_POCKET_H))
    return [prism(Pos(*edge_point(e, p, MAG_OFF)) * Circle(MAG_POCKET_D / 2), z0, z1) for e, p in MAGNETS]


def check_magnet_clearance():
    """Every magnet must keep >= 1 mm of wall from tab pockets and the outside."""
    pockets = []
    for t in layout()[2]:
        c, w = (t["a"] + t["b"]) / 2, t["b"] - t["a"] + 2 * TAB_POCKET_CLEAR
        pockets.append((t["edge"], c - w / 2, c + w / 2))
    for e, p in MAGNETS:
        for pe, a, b in pockets:
            if pe == e:
                gap = max(a - p, p - b) - MAG_POCKET_D / 2
                assert gap >= 1.0, f"magnet {e}@{p} only {gap:.2f} mm from a tab pocket"
        outer = OUTER_SIDE if e in ("left", "right") else OUTER_OFF
        assert outer - MAG_OFF - MAG_POCKET_D / 2 >= 1.0, f"magnet {e}@{p} too close to the outside"
    assert MAG_OFF - MAG_POCKET_D / 2 - TOP_POCKET_OFF >= 1.0
    # side walls: at least 2 mm outside the tab pockets
    assert OUTER_SIDE - (TAB_P + TAB_POCKET_CLEAR) >= 2.0


# ---- top case ------------------------------------------------------------------

def key_opening():
    """Key opening: two holes split by the F-row bridge, corners = 2 mm end mill."""
    o = OPENING_OFF
    upper = rect(-o, BRIDGE_Y1, PCB_X1 + o, o, OPENING_R)
    lower = rect(-o, KEY_Y0 - o, PCB_X1 + o, BRIDGE_Y0, OPENING_R)
    return upper + lower


def top_case():
    body = prism(outer_face(), SPLIT_Z, TOP_Z)
    body = fillet(body.edges().group_by(Axis.Z)[-1], TOP_EDGE_FILLET)
    body -= prism(key_opening(), SPLIT_Z - 1, TOP_Z + 1)
    body -= prism(pcb_offset(TOP_POCKET_OFF, CAV_R + TOP_POCKET_OFF - CAV_GAP), SPLIT_Z - 1, TOP_LEDGE_Z)
    for p in tab_pockets(SPLIT_Z - 1, TOP_LEDGE_Z):
        body -= p
    for m in magnet_pockets(SPLIT_Z, +1):
        body -= m
    return body


# ---- bottom case ---------------------------------------------------------------

def desk_plane():
    """The desk, in the keyboard frame. Thinnest floor (MIN_FLOOR) is at the cavity front."""
    y_cf = PCB_Y0 - CAV_GAP
    origin = Vector(0, y_cf, FLOOR_Z - MIN_FLOOR)
    normal = Vector(0, math.sin(TILT), math.cos(TILT))
    # move the plane so it passes MIN_FLOOR below the floor along its own normal
    return Plane(origin=origin, z_dir=normal)


def bottom_case():
    """The bottom case: a wedge whose underside is one flat face at 8 deg, with the rubber feet recesses."""
    lip_top = SPLIT_Z + LIP_H
    body = prism(outer_face(), -60, SPLIT_Z)
    lip = pcb_offset(LIP_OFF1, CAV_R + LIP_OFF1 - CAV_GAP) - pcb_offset(LIP_OFF0, CAV_R)
    body += prism(lip, SPLIT_Z, lip_top)
    body = split(body, bisect_by=desk_plane(), keep=Keep.TOP)

    body -= prism(pcb_offset(CAV_GAP, CAV_R), FLOOR_Z, lip_top + 1)
    for p in tab_pockets(BOT_LEDGE_Z, lip_top + 1):
        body -= p
    for m in magnet_pockets(SPLIT_Z, -1):
        body -= m

    # USB-C, all cut from the back face:
    #   - a thin skin in front of the receptacle hides the cavity, with a port-shaped hole
    #   - an overmold-sized slot runs from the back face to just short of the mouth
    def usb_plane(y):
        return Plane(origin=(USB_X, y, USB_Z), x_dir=(1, 0, 0), z_dir=(0, 1, 0))

    skin_y0 = PCB_Y1 + USB_SKIN_GAP
    body += prism(rect(USB_X - USB_SKIN_W / 2, skin_y0, USB_X + USB_SKIN_W / 2, PCB_Y1 + CAV_GAP + 0.5),
                  FLOOR_Z, SPLIT_Z)
    slot_y0 = USB_MOUTH_Y + USB_SLOT_STOP
    body -= extrude(usb_plane(slot_y0) * SlotOverall(USB_SLOT_W, USB_SLOT_H), OUTER_OFF + 1)
    port = SlotOverall(USB_PORT_W + 2 * USB_PORT_CLEAR, USB_PORT_H + 2 * USB_PORT_CLEAR)
    body -= extrude(usb_plane(skin_y0 - 1) * port, slot_y0 - skin_y0 + 2)

    # pry notch at the parting line, to lift the magnetic top case off
    body -= prism(edge_rect(PRY_EDGE, PRY_X, PRY_W, -(OUTER_OFF - PRY_DEPTH), OUTER_OFF + 1, 1.4),
                  SPLIT_Z - PRY_H, lip_top + 1)

    # rubber feet: shallow round recesses in the angled underside
    plane = desk_plane()
    for fx, fy in foot_positions():
        p = foot_point(fx, fy)
        body -= Plane(origin=p, z_dir=plane.z_dir) * Cylinder(FOOT_D / 2, 2 * FOOT_DEPTH)
    return body


def foot_point(x, y, pl=None):
    """Point on the desk plane `pl` (default: desk_plane()) above/below (x, y) of the keyboard frame."""
    pl = pl or desk_plane()
    o, n = pl.origin, pl.z_dir
    z = o.Z - ((x - o.X) * n.X + (y - o.Y) * n.Y) / n.Z
    return Vector(x, y, z)


def foot_positions():
    ix, iy = FOOT_INSET - OUTER_SIDE, FOOT_INSET - OUTER_OFF
    return [(PCB_X0 + ix, PCB_Y0 + iy), (PCB_X1 - ix, PCB_Y0 + iy),
            (PCB_X0 + ix, PCB_Y1 - iy), (PCB_X1 - ix, PCB_Y1 - iy)]


# ---- placement in the world (desk = XY plane) ------------------------------------

def to_world(shape, pl=None):
    """Tilt the keyboard frame by 8 deg (back up) and drop it onto the desk `pl` (z = 0)."""
    pl = pl or desk_plane()
    tilted = Rot(TILT_DEG, 0, 0) * shape
    # the desk plane origin, rotated, gives the desk height in the tilted frame
    desk_z = (Rot(TILT_DEG, 0, 0) * Pos(pl.origin)).position.Z
    return Pos(0, 0, -desk_z) * tilted


if __name__ == "__main__":
    check_magnet_clearance()
    t = top_case()
    b = bottom_case()
    print("top", t.bounding_box().size, "valid", t.is_valid, "vol", round(t.volume))
    print("bottom", b.bounding_box().size, "valid", b.is_valid, "vol", round(b.volume))
    bw = to_world(b)
    print("bottom world bbox", bw.bounding_box().min, bw.bounding_box().max)
