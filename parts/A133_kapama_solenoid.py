def build(d, G, g):
    # lokal orijin = kartus govde ucu yuzu merkezi, bobin +Y yonunde; DIN konnektor +Z
    c, k = d["coil"], d["connector"]
    s = [g.cyl(c["d"] / 2, c["len"], "y", center=False),
         g.move(g.box(k["size_x"], k["size_y"], k["size_z"]), 0, k["y_center"], c["d"] / 2 + k["size_z"] / 2 - 2)]
    return g.fuse(*s)
