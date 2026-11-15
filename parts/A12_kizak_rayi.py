def build(d, G, g):
    L, W, H = d["length"], d["width_y"], d["height"]
    s = g.move(g.box(L, W, H), L / 2, 0, H / 2)
    bh = d.get("bolt_holes")
    if bh:
        n = int(L // bh["pitch"])
        off = (L - (n - 1) * bh["pitch"]) / 2
        holes = [g.move(g.cyl(bh["d"] / 2, H + 2, "z"), off + i * bh["pitch"], 0, H / 2) for i in range(n)]
        s = g.cut(s, *holes)
    return s
