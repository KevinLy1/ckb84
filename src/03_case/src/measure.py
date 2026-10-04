"""Key dimensions of the finished keyboard, printed for the documentation."""
import math

from build123d import *

from params import *
import case
from plate import layout

top, bottom = case.top_case(), case.bottom_case()
tw, bw = case.to_world(top), case.to_world(bottom)
asm = Compound([tw, bw])
bb = asm.bounding_box()
print(f"overall W x D x H (desk): {bb.size.X:.1f} x {bb.size.Y:.1f} x {bb.size.Z:.1f}")


def world_z(x, y, z):
    return case.to_world(Pos(x, y, z)).position


front_y, back_y = PCB_Y0 - OUTER_OFF, PCB_Y1 + OUTER_OFF
print(f"front edge height: {world_z(0, front_y, TOP_Z).Z:.1f}")
print(f"back edge height:  {world_z(0, back_y, TOP_Z).Z:.1f}")
home = world_z(0, -3.75 * U, PLATE_Z1)
print(f"plate top at home row (row 3) above desk: {home.Z:.1f}")
print(f"plate top at front row: {world_z(0, -5.75 * U, PLATE_Z1).Z:.1f}")
print(f"split line height front/back: {world_z(0, front_y, SPLIT_Z).Z:.1f} / {world_z(0, back_y, SPLIT_Z).Z:.1f}")
print(f"case outline (machining frame): {PCB_X1 + 2 * OUTER_SIDE:.1f} x {PCB_Y1 - PCB_Y0 + 2 * OUTER_OFF:.2f}")
print(f"top case thickness: {TOP_Z - SPLIT_Z:.1f}")
bbb = bottom.bounding_box()
print(f"bottom case block (machining frame): {bbb.size.X:.1f} x {bbb.size.Y:.1f} x {bbb.size.Z:.1f}")
print(f"bottom case floor under cavity, front / back: {MIN_FLOOR:.1f} / "
      f"{MIN_FLOOR + (PCB_Y1 - PCB_Y0 + 2 * CAV_GAP) * math.tan(TILT) / 1:.1f} (approx)")
print(f"opening: {PCB_X1 + 2 * OPENING_OFF:.1f} x {6.25 * U + 2 * OPENING_OFF:.2f}")
print(f"bridge: y {BRIDGE_Y0:.3f}..{BRIDGE_Y1:.3f}  width {BRIDGE_Y1 - BRIDGE_Y0:.2f}")
rho = 1.05e-3  # ABS g/mm^3
print(f"mass ABS: top {top.volume * rho:.0f} g, bottom {bottom.volume * rho:.0f} g")
print(f"angle check: {math.degrees(math.atan2(world_z(0, back_y, TOP_Z).Z - world_z(0, front_y, TOP_Z).Z, bb.size.Y)):.2f} deg")
pb = layout()
print(f"plate tabs: {len(pb[2])}; gasket pieces: {2 * len(pb[2])}")
fp = [case.foot_point(*p) for p in case.foot_positions()]
print("feet (world xy):", [(round(case.to_world(Pos(p)).position.X, 1), round(case.to_world(Pos(p)).position.Y, 1)) for p in fp])
