"""Switch and stabilizer geometry read from the KiCad board, in the keyboard frame."""
import math
from pathlib import Path

from kicad_parse import load, footprints, pads
from params import from_kicad

ROOT = Path(__file__).resolve().parent.parent
BOARD = ROOT.parent / "02_pcb" / "ckb84.kicad_pcb"


def _pad_offset(fp, p):
    """Pad position relative to the footprint origin, KiCad axes (y down)."""
    a = math.radians(fp["rot"])
    return (p["x"] * math.cos(a) + p["y"] * math.sin(a),
            -p["x"] * math.sin(a) + p["y"] * math.cos(a))


def read():
    fps = footprints(load(BOARD))
    switches = []
    for f in fps:
        if "SW_MX" in f["lib"]:
            x, y = from_kicad(f["x"], f["y"])
            switches.append(dict(ref=f["ref"], x=x, y=y))

    stabs = []
    for f in fps:
        if "STAB_MX" not in f["lib"]:
            continue
        holes = [(_pad_offset(f, p), p["drill"]) for p in pads(f) if p["drill"]]
        big = [o for o, d in holes if d > 3.5]       # 3.99 mm housing holes
        small = [o for o, d in holes if d < 3.5]     # 3.05 mm holes
        sides = []
        for b in big:
            s = min(small, key=lambda o: (o[0] - b[0]) ** 2 + (o[1] - b[1]) ** 2)
            # housing axis points from the small hole to the big hole
            dx, dy = b[0] - s[0], b[1] - s[1]
            n = math.hypot(dx, dy)
            ux, uy = dx / n, dy / n
            mx, my = (b[0] + s[0]) / 2, (b[1] + s[1]) / 2
            cx, cy = mx + ux * 0.885, my + uy * 0.885
            gx, gy = from_kicad(f["x"] + cx, f["y"] + cy)
            # axis_y: housing runs front-to-back (normal 2u/6u); False for the ISO stab
            sides.append(dict(x=gx, y=gy, axis_y=abs(uy) > abs(ux),
                              towards=(round(ux), round(-uy))))
        cx, cy = from_kicad(f["x"], f["y"])
        stabs.append(dict(ref=f["ref"], x=cx, y=cy, kind=f["lib"].split(":")[1], sides=sides))
    return switches, stabs


def kicad_part(ref):
    f = next(f for f in footprints(load(BOARD)) if f["ref"] == ref)
    return from_kicad(f["x"], f["y"])


if __name__ == "__main__":
    sw, st = read()
    print(len(sw), "switches")
    for s in st:
        print(s["ref"], s["kind"], round(s["x"], 2), round(s["y"], 2),
              [(round(d["x"], 2), round(d["y"], 2), d["towards"]) for d in s["sides"]])
