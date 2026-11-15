def _link(d, g, xs):
    L = max(xs); t = d["thickness_y"]; w = d["width_in_plane"]; r = d["end_radius"]
    s = g.fuse(g.move(g.box(L, t, w), L / 2, 0, 0),
               g.cyl(r, t, "y"), g.move(g.cyl(r, t, "y"), L, 0, 0))
    for x in xs:
        s = g.cut(s, g.move(g.cyl(d["holes_d"] / 2, t + 2, "y"), x, 0, 0))
    return s


def build(d, G, g):
    return _link(d, g, [0, d["hole_E_distance_from_A"], d["center_distance_A_B"]])
