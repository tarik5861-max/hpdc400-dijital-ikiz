def build(d, G, g):
    p = d["plate"]; t = p["thickness"]
    s = g.move(g.box(t, *p["size_yz"]), t / 2, 0, 0)
    gh = d["guide_holes"]
    for y, z in gh["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(gh["d"] / 2, t + 2, "x"), t / 2, y, z))
    er = d["ejector_rods"]; L = er["length"]
    for y, z in er["centers_yz"]:
        s = g.fuse(s, g.move(g.cyl(er["d"] / 2, L, "x"), -L / 2, y, z))
    return s
