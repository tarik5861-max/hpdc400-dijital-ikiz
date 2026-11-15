def build(d, G, g):
    p = g.gear_x(d["teeth"], d["module"], 0, d["width"], 0.0, d["phase_deg"], 0, 0)
    a, b = d["shaft_local_x"]
    sh = g.move(g.cyl(d["shaft_d"] / 2, b - a + 1, "x", center=False), a - 1)
    return g.fuse(p, sh)
