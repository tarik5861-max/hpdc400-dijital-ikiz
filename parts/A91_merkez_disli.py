def build(d, G, g):
    # lokal: disli merkezi makine ekseni, -X yuzu, genislik +X
    s = g.gear_x(d["teeth"], d["module"], 0, d["width"], d["bore_d"], d["phase_deg"], 0, 0)
    lh = d.get("lightening_holes")
    if lh:
        import math
        for k in range(lh["count"]):
            a = 2 * math.pi * k / lh["count"]
            h = g.cyl(lh["d"] / 2, d["width"] + 2, "x", center=False)
            h = g.move(h, -1, lh["pcd"] / 2 * math.cos(a), lh["pcd"] / 2 * math.sin(a))
            s = g.cut(s, h)
    return s
