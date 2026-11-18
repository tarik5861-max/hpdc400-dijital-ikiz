def build(d, G, g):
    # lokal orijin: arka plaka arka yuz merkezi; govde -X (x -55..0)
    b = d["back_plate"]; r = d["retainer_plate"]
    x0b, x1b = b["local_x_range"]; x0r, x1r = r["local_x_range"]
    back = g.move(g.box(b["thickness"], *b["size_yz"]), (x0b + x1b) / 2, 0, 0)
    ret = g.move(g.box(r["thickness"], *r["size_yz"]), (x0r + x1r) / 2, 0, 0)
    for key in ("pin_holes", "return_pin_holes"):
        h = d[key]
        for y, z in h["centers_yz"]:
            ret = g.cut(ret, g.move(g.cyl(h["d"] / 2, r["thickness"] + 2, "x"), (x0r + x1r) / 2, y, z))
            # havsa: tutucu plaka arka yuzunde (x1r) cb_depth kadar
            ret = g.cut(ret, g.move(g.cyl(h["cb_d"] / 2, h["cb_depth"], "x"), x1r - h["cb_depth"] / 2, y, z))
    return g.fuse(back, ret)
