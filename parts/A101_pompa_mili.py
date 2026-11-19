# A101 Pompa mili (4520VQ): kamali on uc (kaplin, kampana icinde), 45VQ ve 20VQ rotorlari icin kademeli kamali (spline) bolgeler.
# Lokal orijin: mil on ucu (motor tarafi) merkezi, eksen +X.
import math


def build(d, G, g):
    segs = d["segments"]
    s = None
    for sg in segs:
        a, b = sg["local_x_range"]
        c = g.move(g.cyl(sg["d"] / 2, b - a, "x", center=False), a, 0, 0)
        s = c if s is None else g.fuse(s, c)
    k = d["keyway"]
    a, b = k["local_x_range"]
    r0 = segs[0]["d"] / 2
    s = g.cut(s, g.move(g.box(b - a, k["width"], 2 * k["depth"]), (a + b) / 2, 0, r0))
    for sp in d["splines"]:
        a, b = sp["local_x_range"]
        r = sp["d"] / 2
        for i in range(sp["teeth"]):
            gr = g.move(g.box(b - a, sp["groove_w"], 2 * sp["groove_depth"]), (a + b) / 2, 0, r)
            s = g.cut(s, g.rot(gr, "x", 360.0 * i / sp["teeth"]))
    return s
