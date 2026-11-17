def build(d, G, g):
    # lokal: arka yuz merkezi, x 0..thickness
    t = d["thickness"]
    s = g.move(g.box(t, d["width_y"], d["height_z"]), t / 2)
    sb = d["sleeve_bore"]
    cy, cz = sb["center_yz"]
    bore = g.move(g.cyl(sb["d"] / 2, t + 2, "x", center=False), -1, cy, cz)
    s = g.cut(s, bore)
    if "ejector_holes" in d:
        eh = d["ejector_holes"]
        for y, z in eh["centers_yz"]:
            s = g.cut(s, g.move(g.cyl(eh["d"] / 2, t + 2, "x", center=False), -1, y, z))
    return s
