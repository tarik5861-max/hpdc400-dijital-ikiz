def build(d, G, g):
    f = d["flange"]; ba = d["barrel"]; cap = d["rear_cap"]; rod = d["rod"]
    ft = f["thickness"]; fy, fz = f["size_yz"]
    x0, x1 = ba["local_x_range"]
    s = g.move(g.box(ft, fy, fz), ft / 2, 0, 0)
    bh = f["bolt_holes"]; p = bh["square_pitch"] / 2
    for y in (p, -p):
        for z in (p, -p):
            s = g.cut(s, g.move(g.cyl(bh["d"] / 2, ft + 2, "x"), ft / 2, y, z))
    s = g.fuse(s, g.move(g.tube(ba["od"] / 2, ba["bore"] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0))
    s = g.fuse(s, g.move(g.cyl(cap["od"] / 2, cap["thickness"], "x"), x1 + cap["thickness"] / 2, 0, 0))
    ph = 60.0
    s = g.fuse(s, g.move(g.cyl(ba["bore"] / 2 - 2, ph, "x"), x1 - ph / 2, 0, 0))
    r0 = -rod["exposed_length_toward_minus_x"]; r1 = x1 - ph
    s = g.fuse(s, g.move(g.cyl(rod["d"] / 2, r1 - r0, "x"), (r0 + r1) / 2, 0, 0))
    return s
