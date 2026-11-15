def build(d, G, g):
    # lokal: +X yuzu merkezi, govde x -thickness..0
    t = d["thickness"]
    body = g.cyl(d["od"] / 2, t, "x", center=False)
    body = g.move(body, -t)
    bore = g.move(g.cyl(d["bore_d"] / 2, t + 2, "x", center=False), -t - 1)
    return g.cut(body, bore)
