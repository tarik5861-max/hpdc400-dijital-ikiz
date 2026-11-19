def build(d, G, g):
    # lokal orijin = vurus ekseni yuksekligi (pos Z = shot z_sel); blok A54 arka kafasi ustunde, x/y merkezli
    b, v = d["block"], d["servo_valve"]
    z0, z1 = b["z_range"]
    s = [g.move(g.box(b["len_x"], b["width_y"], z1 - z0), 0, 0, (z0 + z1) / 2)]
    fx, fz = v["flange_xz"]
    y0 = b["width_y"] / 2
    s.append(g.move(g.box(fx, v["flange_t"], fz), 0, y0 + v["flange_t"] / 2, v["z_center"]))
    s.append(g.move(g.cyl(v["body_d"] / 2, v["body_len"], "y", center=False), 0, y0 + v["flange_t"], v["z_center"]))
    return g.fuse(*s)
