def build(d, G, g):
    t, r, c = d["tip"], d["rod"], d["coupling"]
    def seg(dia, x0, x1):
        return g.move(g.cyl(dia / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    x = -t["length"]
    parts = [seg(t["d"], x, 0)]
    parts.append(seg(r["d"], x - r["length"], x))
    x -= r["length"]
    parts.append(seg(c["d"], x - c["length"], x))
    return g.fuse(*parts)
