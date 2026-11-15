def build(d, G, g):
    r0, r1 = d["rod"]["local_x_range"]; p0, p1 = d["piston"]["local_x_range"]
    rod = g.move(g.cyl(d["rod"]["d"] / 2, r1 - r0, "x"), (r0 + r1) / 2, 0, 0)
    pis = g.move(g.cyl(d["piston"]["d"] / 2, p1 - p0, "x"), (p0 + p1) / 2, 0, 0)
    return g.fuse(rod, pis)
