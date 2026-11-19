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
    shell = g.cut(shell, op)
    # tank erisim acikligi (yan duvar, A61 sase icinde) - opsiyonel
    ta = d.get("tank_access_opening")
    if ta:
        x0, x1 = ta["x_range"]
        z0, z1 = ta["local_z_range"]
        ys = -1 if ta["side"] == "-Y" else 1
        yc = ys * (W / 2 - sw / 2)
        shell = g.cut(shell, g.move(g.box(x1 - x0, sw + 2, z1 - z0), (x0 + x1) / 2, yc, (z0 + z1) / 2))
    # boru gecis delikleri: axis "x" (uc plakasi / enine kaburga, x_range + y) ya da "y" (yan duvar, y_range + x)
    for p in d.get("pipe_passages", []):
        if p.get("axis", "x") == "y":
            y0, y1 = p["y_range"]
            hole = g.move(g.cyl(p["d"] / 2, y1 - y0, "y", center=False), p["x"], y0, p["local_z"])
        else:
            x0, x1 = p["x_range"]
            hole = g.move(g.cyl(p["d"] / 2, x1 - x0, "x", center=False), x0, p["y"], p["local_z"])
        shell = g.cut(shell, hole)
    return shell
