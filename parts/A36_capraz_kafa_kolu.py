def build(d, G, g):
    L = d["center_distance_E_D"]; t = d["thickness_y"]; w = d["width_in_plane"]; r = d["end_radius"]
    s = g.fuse(g.move(g.box(L, t, w), L / 2, 0, 0),
               g.cyl(r, t, "y"), g.move(g.cyl(r, t, "y"), L, 0, 0))
    for x in (0, L):
        s = g.cut(s, g.move(g.cyl(d["holes_d"] / 2, t + 2, "y"), x, 0, 0))
    return s
