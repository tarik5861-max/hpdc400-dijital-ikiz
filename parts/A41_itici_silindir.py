def build(d, G, g):
    # Cift silindirli itici grup: 4 tie post + ortak kopru + her merkezde boru/kapak/piston/kol
    po = d["standoff_posts"]; f = d["flange"]; ba = d["barrel"]; cap = d["rear_cap"]
    rod = d["rod"]; pi = d["piston"]
    px0, px1 = po["local_x_range"]; fx0, fx1 = f["local_x_range"]
    bx0, bx1 = ba["local_x_range"]; cx0, cx1 = cap["local_x_range"]
    rx0, rx1 = rod["local_x_range"]; ix0, ix1 = pi["local_x_range"]
    s = g.move(g.box(fx1 - fx0, f["size_yz"][0], f["size_yz"][1]), (fx0 + fx1) / 2, 0, 0)
    for y, z in po["centers_yz"]:
        s = g.fuse(s, g.move(g.cyl(po["d"] / 2, px1 - px0, "x"), (px0 + px1) / 2, y, z))
    for y, z in d["cylinders"]["centers_yz"]:
        s = g.fuse(s, g.move(g.tube(ba["od"] / 2, ba["bore"] / 2, bx1 - bx0, "x"), (bx0 + bx1) / 2, y, z))
        s = g.fuse(s, g.move(g.cyl(cap["od"] / 2, cx1 - cx0, "x"), (cx0 + cx1) / 2, y, z))
        s = g.fuse(s, g.move(g.cyl(rod["d"] / 2, rx1 - rx0, "x"), (rx0 + rx1) / 2, y, z))
        s = g.fuse(s, g.move(g.cyl(pi["d"] / 2, ix1 - ix0, "x"), (ix0 + ix1) / 2, y, z))
    return s
