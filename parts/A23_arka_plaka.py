def build(d, G, g):
    W, Hz, t = d["width_y"], d["height_z"], d["thickness"]
    s = g.move(g.box(t, W, Hz), t / 2, 0, 0)
    lg = d["toggle_lugs"]
    r = lg["end_radius"]
    lugs, pins = [], []
    for px, pz in lg["pin_center_local_xz"]:
        bx = -px  # px negatif: lug x px..0
        for y0, y1 in lg["y_ranges"]:
            ly, yc = y1 - y0, (y0 + y1) / 2
            lugs.append(g.move(g.box(bx, ly, 2 * r), px + bx / 2, yc, pz))
            lugs.append(g.move(g.cyl(r, ly, "y"), px, yc, pz))
            pins.append(g.move(g.cyl(lg["pin_hole_d"] / 2, ly + 2, "y"), px, yc, pz))
    s = g.fuse(s, *lugs)
    cuts = list(pins)
    tb = d["tie_bar_holes"]
    cuts += [g.move(g.cyl(tb["d"] / 2, t + 2, "x"), t / 2, y, z) for y, z in tb["centers_yz"]]
    ch = d["central_hole"]
    cuts.append(g.move(g.cyl(ch["d"] / 2, t + 2, "x"), t / 2, ch["center_yz"][0], ch["center_yz"][1]))
    return g.cut(s, *cuts)
