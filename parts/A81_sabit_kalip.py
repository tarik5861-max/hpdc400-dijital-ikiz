def build(d, G, g):
    # lokal: arka yuz merkezi, x 0..thickness (ayrim yuzu x=thickness)
    t = d["thickness"]
    s = g.move(g.box(t, d["width_y"], d["height_z"]), t / 2)
    sb = d["sleeve_bore"]
    cy, cz = sb["center_yz"]
    cuts = [g.move(g.cyl(sb["d"] / 2, t + 2, "x", center=False), -1, cy, cz)]

    def pocket(x0, x1, y0, y1, z0, z1):
        # ayrim yuzune (x=t) acik cep; +1 mm tasma ayrim yuzunden disari
        return g.move(g.box(x1 - x0 + 1, y1 - y0, z1 - z0), (x0 + x1 + 1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if "cavity" in d:
        c = d["cavity"]
        cuts.append(pocket(*c["x_range"], *c["y"], *c["z"]))
    for sp in d.get("side_pockets", []):
        cuts.append(pocket(*sp["x_range"], *sp["y"], *sp["z"]))
    cg = d.get("core_guides")
    if cg:   # maca kilavuz delikleri: yan yuzden (|y|=width/2) kavite/cebe, Y ekseni
        yo = d["width_y"] / 2 + 1
        for sy in (1, -1):
            for z in cg["z"]:
                L = yo - cg["y_in"]
                cuts.append(g.move(g.cyl(cg["d"] / 2, L, "y"), cg["x"], sy * (cg["y_in"] + L / 2), z))
    return g.cut(s, *cuts)
