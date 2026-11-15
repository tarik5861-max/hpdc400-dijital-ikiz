def build(d, G, g):
    po = d["standoff_posts"]; f = d["flange"]; ba = d["barrel"]; cap = d["rear_cap"]; rod = d["rod"]
    px0, px1 = po["local_x_range"]; fx0, fx1 = f["local_x_range"]
    bx0, bx1 = ba["local_x_range"]; cx0, cx1 = cap["local_x_range"]
    s = g.move(g.box(fx1 - fx0, f["size_yz"][0], f["size_yz"][1]), (fx0 + fx1) / 2, 0, 0)
    for y, z in po["centers_yz"]:
        s = g.fuse(s, g.move(g.cyl(po["d"] / 2, px1 - px0, "x"), (px0 + px1) / 2, y, z))
    s = g.fuse(s, g.move(g.tube(ba["od"] / 2, ba["bore"] / 2, bx1 - bx0, "x"), (bx0 + bx1) / 2, 0, 0))
    s = g.fuse(s, g.move(g.cyl(cap["od"] / 2, cx1 - cx0, "x"), (cx0 + cx1) / 2, 0, 0))
    pist = 30.0
    r0 = rod["local_x_range"][0]; r1 = bx1 - pist
    s = g.fuse(s, g.move(g.cyl(rod["d"] / 2, r1 - r0, "x"), (r0 + r1) / 2, 0, 0))
    s = g.fuse(s, g.move(g.cyl(ba["bore"] / 2 - 2, pist, "x"), bx1 - pist / 2, 0, 0))
    return s
