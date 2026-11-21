def _port(g, p, r):
    # govde yuzeyine +Z / +-Y port: boss 6 mm gomulu (egri yuzey), port boss yuzunden iceri
    f, x, c, bd, bh, pd, dp = p["face"], p["x"], p["c"], p["boss_d"], p["boss_h"], p["port_d"], p["port_depth"]
    ax = "z" if f[1] == "Z" else "y"
    sg = -1 if f[0] == "-" else 1
    boss = g.cyl(bd / 2, bh + 6, ax)
    hole = g.cyl(pd / 2, dp, ax)
    zb = sg * (r + (bh - 6) / 2)
    zh = sg * (r + bh - dp / 2)
    if ax == "z":
        return g.move(boss, x, c, zb), g.move(hole, x, c, zh)
    return g.move(boss, x, zb, c), g.move(hole, x, zh, c)


def build(d, G, g):
    f, b = d["flange"], d["body"]
    def seg(dia, x0, x1):
        return g.move(g.cyl(dia / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    bosses, holes = [], []
    for p in d.get("ports", []):
        bs, hl = _port(g, p, b["od"] / 2)
        bosses.append(bs)
        holes.append(hl)
    s = g.fuse(seg(f["od"], *f["local_x_range"]), seg(b["od"], *b["local_x_range"]), *bosses)
    return g.cut(s, *holes) if holes else s
