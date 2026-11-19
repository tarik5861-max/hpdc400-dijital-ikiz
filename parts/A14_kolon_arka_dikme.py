def build(d, G, g):
    # tek parca kalin govde: XZ yan profili (Y boyunca ekstrude) ∩ YZ pahli siluet (X boyunca ekstrude)
    b = d["body"]
    y0, y1 = b["y_range"]
    side = g.polyprism([(-x, z) for x, z in b["profile_xz"]], 0, y1 - y0)
    side = g.move(g.rot(side, "z", 90), 0, y0, 0)
    xs = [x for x, _ in b["profile_xz"]]
    zt = max(z for _, z in b["profile_xz"])
    c = b["top_corner_chamfer"]
    pts = [(y0, 0), (y1, 0), (y1, zt - c), (y1 - c, zt), (y0 + c, zt), (y0, zt - c)]
    sil = g.polyprism(pts, min(xs) - 1, max(xs) + 1)
    return g.common(side, sil)
