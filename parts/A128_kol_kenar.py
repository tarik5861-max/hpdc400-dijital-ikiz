# A128 Kapi kolu (+Y yuz, dusey tutamak) + mekanik koruyucu kenar (alu tutucu + yumusak lastik tampon, on kenar).
# Lokal orijin A71 ile AYNI.


def _bx(g, x0, x1, y0, y1, z0, z1):
    s = g.box(x1 - x0, y1 - y0, z1 - z0)
    return g.move(s, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def build(d, G, g):
    dr = d["door"]
    H = dr["height"]
    h = dr["thickness_y"] / 2
    hd = d["handle"]
    eg = d["edge_guard"]

    xh = hd["x"]
    z0, z1 = hd["z_range"]
    y0 = h
    ys = y0 + hd["standoff"]
    r = hd["bar_d"] / 2
    bar = g.move(g.cyl(r, z1 - z0, "z"), xh, ys + r, (z0 + z1) / 2)
    out = [bar]
    for zz in (z0 + hd["inset"], z1 - hd["inset"]):
        so = g.cyl(hd["standoff_d"] / 2, hd["standoff"] + r, "y")
        out.append(g.move(so, xh, y0 + (hd["standoff"] + r) / 2, zz))

    ht = eg["holder_thk"]
    out.append(_bx(g, -ht, 0, -h, h, 0, H))
    br = eg["bumper_d"] / 2
    out.append(g.move(g.cyl(br, H, "z"), -ht - br, 0, H / 2))
    return g.fuse(*out)
