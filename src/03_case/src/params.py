"""All design dimensions (mm). Frame: "keyboard frame" = plate frame before tilting.

  x  -> right, origin at the left edge of the key area
  y  -> back (towards the USB port), origin at the top edge of the key area (row 0 top)
  z  -> up, origin at the PCB top surface

The finished keyboard is this frame rotated +8 deg about X (back edge raised).
"""
import math

U = 19.05  # key pitch

# ---- KiCad -> keyboard frame -------------------------------------------------
KX0 = 49.480724   # KiCad x of the left board edge
KY0 = 50.973335   # KiCad y of the top edge of the key area


def from_kicad(kx, ky):
    return kx - KX0, KY0 - ky


# ---- PCB ---------------------------------------------------------------------
PCB_X0, PCB_X1 = 0.0, 304.8
PCB_Y0, PCB_Y1 = KY0 - 170.015835, KY0 - 46.228335   # -119.04 .. +4.745
PCB_T = 1.51            # board thickness from the KiCad STEP export
PCB_BOTTOM_PARTS = 3.3  # tallest bottom-side part (USB-C receptacle)

# ---- Plate -------------------------------------------------------------------
PLATE_T = 1.5
PLATE_Z0 = 3.5                     # MX standard: plate bottom 3.5 above PCB top
PLATE_Z1 = PLATE_Z0 + PLATE_T      # 5.0
PLATE_CORNER_R = 1.0
SW_CUT = 14.0                      # MX switch cutout
SW_CUT_R = 0.5
STAB_CUT_W, STAB_CUT_L = 7.0, 15.0  # Cherry screw-in stab housing cutout
STAB_CUT_SHIFT = 0.885             # cutout centre beyond pad midpoint, towards the 3.99 mm hole
TAB_W = U - 1.2                    # nominal gasket tab width (slots land on key gaps)
TAB_P = 4.5                        # tab protrusion beyond the plate edge
TAB_R = 2.0
RELIEF_W = 1.2                     # flex-relief slot width beside each tab
RELIEF_MAX, RELIEF_MIN = 7.0, 5.0
RELIEF_SEARCH = 3.0                # how far a slot may move to find a gap between cutouts
RELIEF_CLEAR = 1.2                 # min web between a relief slot and any cutout

# nominal tab centres: (edge, position along edge); front/side ones sit on key centres
TABS = [("back", 45), ("back", 115), ("back", 190), ("back", 260),
        ("front", 1.75 * U), ("front", 98.0), ("front", 11.25 * U), ("front", 14.5 * U),
        ("left", -2.75 * U), ("right", -2.75 * U)]

# ---- Gaskets -----------------------------------------------------------------
GASKET_T = 3.0           # nominal Poron thickness
GASKET_COMP = 0.20       # 20 % compression
GASKET_GAP = GASKET_T * (1 - GASKET_COMP)   # 2.4
TOP_LEDGE_Z = PLATE_Z1 + GASKET_GAP         # 7.4  underside of top case over tabs
BOT_LEDGE_Z = PLATE_Z0 - GASKET_GAP         # 1.1  bottom-case ledge under tabs

# ---- Case --------------------------------------------------------------------
CAV_GAP = 1.5            # plate/PCB edge -> case inner wall
CAV_R = 3.0
WALL = 8.5               # wall thickness beyond the cavity
OUTER_OFF = CAV_GAP + WALL          # 10.0 from PCB edge, front and back (magnets live here)
OUTER_SIDE = CAV_GAP + 6.0          # 7.5 left and right: only tab pockets, no magnets
OUTER_R = 4.0                       # outer corner radius (plan view)
TOP_EDGE_FILLET = 1.5
SPLIT_Z = PLATE_Z1                  # top/bottom case parting plane
TOP_Z = PLATE_Z1 + 9.0              # 14.0 top surface (high-profile, hides switches)
OPENING_OFF = 0.3                   # key opening beyond the key area (caps sit >= 0.4 inside it)
OPENING_R = 1.0                     # 2 mm end mill
TAB_POCKET_CLEAR = 1.0
LIP_OFF0, LIP_OFF1, LIP_H = CAV_GAP, 2.6, 1.5    # alignment lip on the bottom case
TOP_POCKET_OFF = 2.8                # top-case underside recess (fits over the lip)
FLOOR_Z = -PCB_T - 5.0              # -6.51 cavity floor (parts + case foam)
MIN_FLOOR = 3.0                     # thinnest floor, at the front
TILT_DEG = 8.0
TILT = math.radians(TILT_DEG)

# F-row bridge: hides the 0.25U gap between row 0 and row 1.
# Keycap edges measured on the KiCad 3D model (widest point of the skirts).
CAP_ROW0_FRONT = -18.505            # front edge of the F-row caps
CAP_ROW1_BACK = -24.217             # back edge of the number-row caps
BRIDGE_CLEAR = 0.6
BRIDGE_Y1 = CAP_ROW0_FRONT - BRIDGE_CLEAR              # back edge of the bridge
BRIDGE_Y0 = CAP_ROW1_BACK + BRIDGE_CLEAR               # front edge of the bridge

# ---- USB-C -------------------------------------------------------------------
USB_X = 201.955724 - KX0
# Receptacle front shell, measured on the KiCad 3D model
USB_Z = -3.215                      # mouth centre
USB_MOUTH_Y = 6.41                  # mouth face (beyond the PCB edge)
USB_PORT_W, USB_PORT_H = 8.96, 3.17
# Outer slot for the plug overmold, from the back face to just short of the mouth
USB_SLOT_W, USB_SLOT_H = 13.0, 7.5
USB_SLOT_STOP = 0.3                 # slot ends this far beyond the mouth (overmold face sits ~0.45)
# Inner skin that hides the cavity: wall brought to 1 mm from the PCB edge, with a port-shaped hole
USB_SKIN_GAP = 1.0                  # PCB edge -> skin (the PCB floats on its gaskets)
USB_SKIN_W = 19.0
USB_PORT_CLEAR = 0.5                # around the receptacle shell

# ---- Magnets (5 x 2 mm N52 discs) --------------------------------------------
MAG_D, MAG_H = 5.0, 2.0
MAG_POCKET_D, MAG_POCKET_H = 5.1, 2.1
MAG_OFF = 6.4                       # from PCB edge: 1 mm wall to the recess and to the outside
# 8 pairs, symmetric about the board centre line, one near each corner
MAGNETS = [("back", 10), ("back", 80), ("back", 225), ("back", 295),
           ("front", 10), ("front", 65.7), ("front", 239.1), ("front", 295)]

# ---- Feet (10 x 3 mm round bumpons) ------------------------------------------
FOOT_D, FOOT_DEPTH = 10.4, 1.0
FOOT_INSET = 22.0                   # from outer edges, measured on the underside

# ---- Pry notch (back, bottom case, centred above the USB-C slot) ---------------
PRY_EDGE = "back"
PRY_X, PRY_W, PRY_DEPTH, PRY_H = PCB_X1 / 2, 24.0, 2.0, 1.5

# ---- Reset / boot buttons (bottom side of the PCB, no case access) ------------
RESETS = [(332.43, 71.64), (345.43, 72.58)]   # KiCad coordinates of RST1/RST2 (foam clearance)
