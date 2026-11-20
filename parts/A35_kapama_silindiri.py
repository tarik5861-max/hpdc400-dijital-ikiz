def build(d, G, g):
    f = d["flange"]; ba = d["barrel"]; cap = d["rear_cap"]
    ft = f["thickness"]; fy, fz = f["size_yz"]
    x0, x1 = ba["local_x_range"]
    s = g.move(g.box(ft, fy, fz), ft / 2, 0, 0)
    bh = f["bolt_holes"]; p = bh["square_pitch"] / 2
    for y in (p, -p):
        for z in (p, -p):
            s = g.cut(s, g.move(g.cyl(bh["d"] / 2, ft + 2, "x"), ft / 2, y, z))
    s = g.fuse(s, g.move(g.tube(ba["od"] / 2, ba["bore"] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0))
    s = g.fuse(s, g.move(g.cyl(cap["od"] / 2, cap["thickness"], "x"), x1 + cap["thickness"] / 2, 0, 0))
    # flanstaki kol deliği (d100) boru ile açık birleşir
    s = g.cut(s, g.move(g.cyl(f["rod_hole_d"] / 2, ft + 2, "x"), ft / 2, 0, 0))
    for e in d["ports"]["liste"]:
        x, y, z = e["konum_lokal"]; r = e["d"] / 2; dp = e["derinlik"]
        if e["eksen"] == "z":  # radyal, alt cevreden yukari
            s = g.cut(s, g.move(g.cyl(r, dp + 1, "z", center=False), x, y, z - 1))
        else:  # x=40 arka yuzden flansin icine
            s = g.cut(s, g.move(g.cyl(r, dp, "x", center=False), x - dp, y, z))
    return s
