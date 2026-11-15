def build(d, G, g):
    # lokal: -X yuzu merkezi, govde x 0..thickness
    t = d["thickness"]
    gr = d["gear_ring"]
    x0, x1 = gr["local_x_range"]
    body = g.cyl(d["body_od"] / 2, t, "x", center=False)
    ring = g.move(g.cyl(gr["od"] / 2, x1 - x0, "x", center=False), x0)
    s = g.fuse(body, ring)
    bore = g.move(g.cyl(d["bore_d"] / 2, t + 2, "x", center=False), -1)
    return g.cut(s, bore)
