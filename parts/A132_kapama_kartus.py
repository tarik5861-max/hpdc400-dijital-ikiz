def build(d, G, g):
    # lokal orijin = blok yuzu merkezi, govde +Y yonunde (flans y 0..t, gövde t..t+len)
    f, b = d["flange"], d["body"]
    s = [g.move(g.box(f["size_xz"], f["t"], f["size_xz"]), 0, f["t"] / 2, 0),
         g.move(g.cyl(b["d"] / 2, b["len"], "y", center=False), 0, f["t"], 0)]
    return g.fuse(*s)
