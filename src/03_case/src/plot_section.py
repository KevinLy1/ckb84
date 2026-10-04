import sys; sys.path.insert(0, "src")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from build123d import *
import case, plate as plate_mod
from params import *
x = float(sys.argv[1]) if len(sys.argv) > 1 else 100.0
pl = Plane(origin=(x, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))
fig, ax = plt.subplots(figsize=(16, 6), dpi=110)
for shape, col in [(case.top_case(), "#555"), (case.bottom_case(), "#333"), (plate_mod.plate(), "#c90")]:
    sec = section(case.to_world(shape), pl)
    for e in sec.edges():
        e = pl.to_local_coords(e)
        pts = [e.position_at(t / 20) for t in range(21)]
        ax.plot([p.X for p in pts], [p.Y for p in pts], color=col, lw=1)
ax.set_aspect("equal"); ax.grid(alpha=.3)
fig.savefig(f"out/section_{int(x)}.png", bbox_inches="tight")
