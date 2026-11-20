# A125 Ust ray (kutu profil) + 2 asili makara arabasi (U askı, tekerlek) + 2 ray dikmesi.
# Lokal orijin A71 ile AYNI (panel alt -X ucu, orta Y). Kapi kapali konumda.


def _bx(g, x0, x1, y0, y1, z0, z1):
    s = g.box(x1 - x0, y1 - y0, z1 - z0)
    return g.move(s, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def build(d, G, g):
    tr = d["top_track"]
    hg = d["hanger"]
    wh = d["wheel"]
    ps = d["posts"]

    x0, x1 = tr["x_range"]
    y0, y1 = tr["y_range"]
    z0, z1 = tr["z_range"]
    beam = _bx(g, x0, x1, y0, y1, z0, z1)

    yi = hg["plate_inner_y"]
    yo = yi + hg["plate_thk"]
    hw = hg["plate_x_w"] / 2
    fz0, fz1 = hg["foot_z"]
    out = [beam]
    for xc in hg["x_centers"]:
        out.append(_bx(g, xc - hw, xc + hw, -yo, yo, fz0, fz1))          # baglanti plakasi (kapi ustu)
        out.append(_bx(g, xc - hw, xc + hw, yi, yo, fz1, hg["top_z"]))   # +Y yan plaka
        out.append(_bx(g, xc - hw, xc + hw, -yo, -yi, fz1, hg["top_z"])) # -Y yan plaka
        wz = z1 + wh["d"] / 2
        w = g.cyl(wh["d"] / 2, wh["width"], "y")
        out.append(g.move(w, xc, 0, wz))                                 # tekerlek ray ustunde
        ax = g.cyl(wh["axle_d"] / 2, 2 * yo, "y")
        out.append(g.move(ax, xc, 0, wz))

    # dikmeler: ray -Y yuzune bitisik, alt ray ustunden ray uste
    py0, py1 = ps["y_range"]
    for a, b in ps["x_ranges"]:
        out.append(_bx(g, a, b, py0, py1, ps["z0"], z1))
    return g.fuse(*out)
