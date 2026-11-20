def build(d, G, g):
    L = d["length"]; r = d["d"] / 2
    s = g.cyl(r, L, "x")
    return g.move(s, L / 2, 0, 0)
