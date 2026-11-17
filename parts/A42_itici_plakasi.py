def build(d, G, g):
    p = d["plate"]; t = p["thickness"]
    s = g.move(g.box(t, *p["size_yz"]), t / 2, 0, 0)
    gh = d["guide_holes"]
    cuts = [g.move(g.cyl(gh["d"] / 2, t + 2, "x"), t / 2, y, z) for y, z in gh["centers_yz"]]
    ra = d.get("rod_attach")
    if ra:
        for y, z in ra["centers_yz"]:
            cuts.append(g.move(g.cyl(ra["tapped_d"] / 2, ra["depth"] + 1, "x", center=False),
                               t - ra["depth"], y, z))
    s = g.cut(s, *cuts)
    er = d["ejector_rods"]; L = er["length"]
    for y, z in er["centers_yz"]:
        s = g.fuse(s, g.move(g.cyl(er["d"] / 2, L, "x"), -L / 2, y, z))
    cr = d.get("center_rod")
    if cr:
        cy, cz = cr["center_yz"]
        s = g.fuse(s, g.move(g.cyl(cr["d"] / 2, cr["length"], "x"), -cr["length"] / 2, cy, cz))
    return s
