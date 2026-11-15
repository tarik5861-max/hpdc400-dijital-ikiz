def build(d, G, g):
    h = d["hub"]; t = d["tongue"]; ph = d["pin_D_holes"]
    s = g.fuse(g.box(h["len_x"], h["width_y"], h["height_z"]),
               g.box(t["len_x"], t["width_y"], t["height_z"]))
    for c in ph["centers_local_xz"]:
        s = g.cut(s, g.move(g.cyl(ph["d"] / 2, t["width_y"] + 2, "y"), c[0], 0, c[1]))
    return s
