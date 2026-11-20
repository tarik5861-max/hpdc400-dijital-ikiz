def _stadium(g, lx, wy, h):
    # X boyunca uzun, Z yonunde h yuksekliginde, merkezde (z -h/2..h/2)
    r = wy / 2
    s = g.box(lx - wy, wy, h)
    return g.fuse(s, g.move(g.cyl(r, h, "z"), (lx - wy) / 2, 0, 0), g.move(g.cyl(r, h, "z"), -(lx - wy) / 2, 0, 0))


def build(d, G, g):
    # lokal: A51 dolum agzi merkezi (x,y), vurus ekseni yuksekligi (z=0); taban z=base_z (kamara ust cizgisi)
    z0 = d["base_z"]
    c, f = d["collar"], d["flare"]
    hl, hw = d["hole"]["length_x"], d["hole"]["width_y"]
    col = _stadium(g, hl + 2 * c["wall_x"], hw + 2 * c["wall_y"], c["height"])
    col = g.cut(col, _stadium(g, hl, hw, c["height"] + 2))
    col = g.move(col, 0, 0, z0 + c["height"] / 2)
    fl = _stadium(g, f["outer_len"], f["outer_w"], f["height"])
    fl = g.cut(fl, _stadium(g, f["hole_len"], f["hole_w"], f["height"] + 2))
    fl = g.move(fl, 0, 0, z0 + c["height"] + f["height"] / 2)
    return g.fuse(col, fl)
