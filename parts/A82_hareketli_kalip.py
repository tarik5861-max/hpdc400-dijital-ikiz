def build(d, G, g):
    # lokal: arka yuz merkezi, x -thickness..0; ayrim yuzu x=-thickness
    t = d["thickness"]
    s = g.move(g.box(t, d["width_y"], d["height_z"]), -t / 2)
    cuts = []
    p = d["cavity_pocket"]
    py, pz = p["size_yz"]
    cy, cz = p["center_yz"]
    cuts.append(g.move(g.box(p["depth"] + 1, py, pz), -t + (p["depth"] - 1) / 2, cy, cz))
    r = d["runner_groove"]
    z0, z1 = r["from_yz"][1], r["to_yz"][1]
    cuts.append(g.move(g.box(r["depth"] + 1, r["width"], abs(z1 - z0)),
                       -t + (r["depth"] - 1) / 2, r["from_yz"][0], (z0 + z1) / 2))
    if "ejector_pin_holes" in d:
        eph = d["ejector_pin_holes"]
        for y, z in eph["centers_yz"]:
            cuts.append(g.move(g.cyl(eph["d"] / 2, t + 2, "x", center=False), -t - 1, y, z))
    return g.cut(s, *cuts)
