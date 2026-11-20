def build(d, G, g):
    # lokal orijin = blok merkezi; x/y/z ekseni global ile paralel. Portlar +X (arka) yuzunde, valfler +-Y yuzlerinde.
    b, p = d["block"], d["ports"]
    L, W, H = b["len_x"], b["width_y"], b["height_z"]
    s = [g.box(L, W, H)]
    for y, z in p["yz"]:  # P/T/A/B kisa tapali stub (+X yuzu)
        s.append(g.move(g.cyl(p["stub_d"] / 2, p["stub_len"], "x", center=False), L / 2, y, z))
    m = p["gauge_port"]   # PT1/manometre portu: ust yuz
    s.append(g.move(g.cyl(m["d"] / 2, m["len"], "z", center=False), m["x"], m["y"], H / 2))
    return g.fuse(*s)
