def build(d, G, g):
    # lokal: global eksenlere paralel, orijin = tup sirasi ekseni (X=-3020,Y=0,Z=0).
    # Sert boru (eksenel parcalar): tup uclarindan yukari -> toplayici (Y boyunca) -> A54 arka kafasina (+X, sonra asagi)
    ys, zs, zh = d["risers_y"], d["z_riser_start"], d["z_header"]
    rr, rh, rm = d["riser_d"] / 2, d["header_d"] / 2, d["main_d"] / 2
    parts = [g.move(g.cyl(rr, zh - zs + rh, "z", center=False), 0, y, zs) for y in ys]
    y0, y1 = min(ys), max(ys)
    parts.append(g.move(g.cyl(rh, y1 - y0 + 2 * rh, "y", center=False), 0, y0 - rh, zh))
    m = d["main_run"]
    parts.append(g.move(g.cyl(rm, m["x_end_local"] + rm, "x", center=False), 0, m["y"], zh))
    parts.append(g.move(g.cyl(rm, zh - m["z_end"] + rm, "z", center=False), m["x_end_local"], m["y"], m["z_end"]))
    return g.fuse(*parts)
