def build(d, G, g):
    # lokal orijin: A54 on kafa on yuzu (X), sensor ekseni (Y=0), vurus ekseni yuksekligi (Z=0); +X yonunde tup
    br, tb, fl, ls = d["bracket"], d["tube"], d["float"], d["ls2"]
    x0, x1 = br["x"]
    s = [g.move(g.box(x1 - x0, 2 * br["half_y"], 2 * br["half_z"]), (x0 + x1) / 2, 0, 0)]
    t0, t1 = tb["x_range"]
    s.append(g.move(g.cyl(tb["d"] / 2, t1 - t0, "x"), (t0 + t1) / 2, 0, 0))
    # mikne/yuzer: tup uzerinde, kolla A52 kaplinine (Y=-arm_y) bagli; geri cekik pozisyonda cizilir
    s.append(g.move(g.tube(fl["od"] / 2, tb["d"] / 2 + 0.5, fl["len"], "x"), fl["x_center"], 0, 0))
    ay = fl["arm_y_to_coupling"]
    s.append(g.move(g.box(fl["len"], ay - fl["od"] / 2 + 5, fl["arm_w"]), fl["x_center"], -(ay + fl["od"] / 2 - 5) / 2, 0))
    a, b = ls["x_range"]
    s.append(g.move(g.box(b - a, ls["size"], ls["size"]), (a + b) / 2, 0, 0))
    return g.fuse(*s)
