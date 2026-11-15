import math


def build(d, G, g):
    b = d["body"]; arms = d["integral_link_arms"]
    s = g.box(b["len_x"], b["width_y"], b["height_z"])
    t = arms["thickness_y"]; w = arms["bar_width_in_plane"]; er = arms["eye_radius"]
    L = arms["center_distance"]
    for sgn in (1, -1):
        D = arms["D_local_xz"][0 if sgn == 1 else 1]
        E = arms["E_local_xz"][0 if sgn == 1 else 1]
        ang = math.degrees(math.atan2(-(E[1] - D[1]), E[0] - D[0]))  # Ry: (1,0)->(cos,-sin)
        bar = g.rot(g.box(L, t, w), "y", ang)
        bar = g.move(bar, (D[0] + E[0]) / 2, 0, (D[1] + E[1]) / 2)
        s = g.fuse(s, bar, g.move(g.cyl(er, t, "y"), E[0], 0, E[1]))
    for c in d["pin_D_holes"]["centers_local_xz"]:
        s = g.cut(s, g.move(g.cyl(d["pin_D_holes"]["d"] / 2, b["width_y"] + 2, "y"), c[0], 0, c[1]))
    for c in arms["E_local_xz"]:
        s = g.cut(s, g.move(g.cyl(arms["E_hole_d"] / 2, t + 2, "y"), c[0], 0, c[1]))
    return s
