def build(d, G, g):
    L = d["length"]
    s = g.cyl(d["tube_od"] / 2, L, "x", center=False)
    for a, b in (d["lip1_local_x"], d["lip2_local_x"]):
        s = g.fuse(s, g.move(g.cyl(d["lip_od"] / 2, b - a, "x", center=False), a))
    return g.cut(s, g.move(g.cyl(d["tube_id"] / 2, L + 2, "x", center=False), -1))
