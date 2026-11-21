def build(d, G, g):
    t, r, c = d["tip"], d["rod"], d["coupling"]
    def seg(dia, x0, x1):
        return g.move(g.cyl(dia / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    x = -t["length"]
    parts = [seg(t["d"], x, 0)]
    parts.append(seg(r["d"], x - r["length"], x))
    x -= r["length"]
    parts.append(seg(c["d"], x - c["length"], x))
    s = g.fuse(*parts)
    w = d.get("water")
    if not w:
        return s
    # su yolu: kor delik + ic besleme borusu (tup-ici-tup) + coupling'de radyal giris/cikis (temsili)
    bx0, bx1 = w["bore_x"]
    tx0, tx1 = w["tube_x"]
    fx0 = w["feed_x"][0]
    s = g.cut(s, seg(w["bore_d"], bx0, bx1))
    s = g.fuse(s, seg(w["tube_od"], tx0, tx1))
    s = g.cut(s, seg(w["tube_id"], fx0, tx1 + 1))                        # besleme kanali: giristen tup ucuna
    rc = c["d"] / 2
    pr = w["port_d"] / 2
    ri = g.move(g.cyl(pr, rc + 2, "y"), w["in_x"], (rc + 2) / 2, 0)                  # +Y giris (besleme kanalina)
    ro0 = w["tube_od"] / 2 + 1
    lo = rc - ro0 + 2
    ro = g.move(g.cyl(pr, lo, "y"), w["out_x"], -(ro0 + lo / 2), 0)                  # -Y cikis (halka kanaldan)
    return g.cut(s, ri, ro)
