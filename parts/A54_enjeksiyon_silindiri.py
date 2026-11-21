def _port(g, p, h):
    # h = kafa yan olcusu (yarim); face +Z / +-Y; boss govdeye 2 mm gomulu, port boss yuzunden iceri
    f, x, c, bd, bh, pd, dp = p["face"], p["x"], p["c"], p["boss_d"], p["boss_h"], p["port_d"], p["port_depth"]
    ax = "z" if f[1] == "Z" else "y"
    sg = -1 if f[0] == "-" else 1
    boss = g.cyl(bd / 2, bh + 2, ax)
    hole = g.cyl(pd / 2, dp, ax)
    zb = sg * (h + (bh - 2) / 2)
    zh = sg * (h + bh - dp / 2)
    if ax == "z":
        return g.move(boss, x, c, zb), g.move(hole, x, c, zh)
    return g.move(boss, x, zb, c), g.move(hole, x, zh, c)


def build(d, G, g):
    fh, ba, rh, rod = d["front_head"], d["barrel"], d["rear_head"], d["rod"]   # rod: yalniz on kafa gecis deligi (kol A186)
    def blk(h):
        x0, x1 = h["local_x_range"]
        return g.move(g.box(x1 - x0, h["size_yz"][0], h["size_yz"][1]), (x0 + x1) / 2, 0, 0)
    x0, x1 = ba["local_x_range"]
    barrel = g.move(g.tube(ba["od"] / 2, ba["bore"] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    bosses, holes = [], []
    for p in d.get("ports", []):
        b, hl = _port(g, p, fh["size_yz"][0] / 2)
        bosses.append(b)
        holes.append(hl)
    fx0, fx1 = fh["local_x_range"]
    holes.append(g.move(g.cyl(rod["d"] / 2, fx1 - fx0, "x"), (fx0 + fx1) / 2, 0, 0))   # kol gecis deligi (A186)
    for p in d.get("ports_x", []):   # on yuz (+X): yalniz delik (flans A183'te)
        holes.append(g.move(g.cyl(p["port_d"] / 2, p["port_depth"], "x"), fx1 - p["port_depth"] / 2, p["y"], p["z"]))
    s = g.fuse(blk(fh), blk(rh), barrel, *bosses)
    return g.cut(s, *holes) if holes else s
