def build(d, G, g):
    W, Hz, t = d["width_y"], d["height_z"], d["thickness"]
    s = g.move(g.box(t, W, Hz), -t / 2, 0, 0)
    tb = d["tie_bar_holes"]
    cuts = [g.move(g.cyl(tb["d"] / 2, t + 2, "x"), -t / 2, y, z) for y, z in tb["centers_yz"]]
    sh = d["shot_hole"]
    cuts.append(g.move(g.cyl(sh["d"] / 2, t + 2, "x"), -t / 2, sh["center_yz"][0], sh["center_yz"][1]))
    if "ejector_return_holes" in d:
        erh = d["ejector_return_holes"]
        for y, z in erh["centers_yz"]:
            cuts.append(g.move(g.cyl(erh["d"] / 2, t + 2, "x"), -t / 2, y, z))
    return g.cut(s, *cuts)
