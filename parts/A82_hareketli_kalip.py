def build(d, G, g):
    # lokal: arka yuz merkezi, x -thickness..0; ayrim yuzu x=-thickness
    t = d["thickness"]
    eb = d["ejector_box"]
    cp = eb["clamping_plate"]; ra = eb["rails"]; cv = eb["cavity_plate"]
    cx0, cx1 = cp["local_x_range"]
    vx0, vx1 = cv["local_x_range"]
    rx0, rx1 = ra["local_x_range"]
    # cavity plate (ayrim yuzu tarafi)
    s = g.move(g.box(vx1 - vx0, *cv["size_yz"]), (vx0 + vx1) / 2)
    # clamping plate (arka)
    clamp = g.move(g.box(cx1 - cx0, *cp["size_yz"]), (cx0 + cx1) / 2)
    ch = [g.move(g.cyl(cp["center_hole_d"] / 2, cx1 - cx0 + 2, "x"), (cx0 + cx1) / 2)]
    eph = d["ejector_pin_holes"]
    for y, z in eph["centers_yz"]:
        ch.append(g.move(g.cyl(eph["d"] / 2, cx1 - cx0 + 2, "x"), (cx0 + cx1) / 2, y, z))
    clamp = g.cut(clamp, *ch)
    s = g.fuse(s, clamp)
    # raylar (kutu bosluğu |Y|<200, Z'ye acik)
    for y0, y1 in ra["y_ranges"]:
        z0, z1 = ra["z_range"]
        s = g.fuse(s, g.move(g.box(rx1 - rx0, y1 - y0, z1 - z0), (rx0 + rx1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    cuts = []
    # cavity plate delikleri
    pb = eb["ejector_pin_bores"]; rb = eb["return_pin_bores"]
    for b in (pb, rb):
        bx0, bx1 = b["local_x_range"]
        for y, z in b["centers_yz"]:
            cuts.append(g.move(g.cyl(b["d"] / 2, bx1 - bx0 + 2, "x"), (bx0 + bx1) / 2, y, z))
    # opsiyonel cep ve yolluk
    if "cavity_pocket" in d:
        p = d["cavity_pocket"]; py, pz = p["size_yz"]; cy, cz = p["center_yz"]
        cuts.append(g.move(g.box(p["depth"] + 1, py, pz), -t + (p["depth"] - 1) / 2, cy, cz))
    for sp in d.get("side_pockets", []):   # A81 yan maca ceplerinin esi (ayrim yuzunde)
        sy0, sy1 = sp["y"]; sz0, sz1 = sp["z"]
        cuts.append(g.move(g.box(sp["depth"] + 1, sy1 - sy0, sz1 - sz0), -t + (sp["depth"] - 1) / 2, (sy0 + sy1) / 2, (sz0 + sz1) / 2))
    if "runner_groove" in d:
        r = d["runner_groove"]; z0, z1 = r["from_yz"][1], r["to_yz"][1]
        cuts.append(g.move(g.box(r["depth"] + 1, r["width"], abs(z1 - z0)),
                           -t + (r["depth"] - 1) / 2, r["from_yz"][0], (z0 + z1) / 2))
    return g.cut(s, *cuts)
