def build(d, G, g):
    # lokal: arka yuz merkezi, x 0..thickness
    t = d["thickness"]
    s = g.move(g.box(t, d["width_y"], d["height_z"]), t / 2)
    sb = d["sleeve_bore"]
    cy, cz = sb["center_yz"]
    bore = g.move(g.cyl(sb["d"] / 2, t + 2, "x", center=False), -1, cy, cz)
    return g.cut(s, bore)
