def build(d, G, g):
    # lokal: -X uc yuzu merkezi, eksen +X, 0..length
    return g.cyl(d["d"] / 2, d["length"], "x", center=False)
