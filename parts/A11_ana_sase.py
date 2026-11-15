def build(d, G, g):
    L, W, H = d["length"], d["width_y"], d["height"]
    xmin, xmax = d["x_min"], d["x_max"]
    tp, sw, ep, rt = d["top_plate_thk"], d["side_wall_thk"], d["end_plate_thk"], d["cross_rib_thk"]
    xc = (xmin + xmax) / 2
    body = g.move(g.box(L, W, H), xc, 0, H / 2)
    # ic bosluk (alt acik): z -1..H-tp
    ih = H - tp
    inner = g.move(g.box(L - 2 * ep, W - 2 * sw, ih + 1), xc, 0, (ih - 1) / 2)
    shell = g.cut(body, inner)
    ribs = []
    for x in d["cross_ribs_x"]:
        ribs.append(g.move(g.box(rt, W - 2 * sw + 2, ih), x, 0, ih / 2))
    shell = g.fuse(shell, *ribs)
    o = d["top_opening_biscuit_drop"]
    ox, oy = o["x_max"] - o["x_min"], o["y_max"] - o["y_min"]
    op = g.move(g.box(ox, oy, tp + 2), (o["x_min"] + o["x_max"]) / 2, (o["y_min"] + o["y_max"]) / 2, H - tp / 2)
    return g.cut(shell, op)
