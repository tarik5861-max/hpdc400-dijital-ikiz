# A127 Kilitli guvenlik limit anahtari: kapali + acik konum govdeleri (alt ray ustunde, -Y seridi) + kapi uzerindeki dil (actuator).
# Lokal orijin A71 ile AYNI. Dil kapi -Y yuzunde; kapi kapali iken kapali anahtara, acik iken acik anahtara girer.


def _bx(g, x0, x1, y0, y1, z0, z1):
    s = g.box(x1 - x0, y1 - y0, z1 - z0)
    return g.move(s, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def build(d, G, g):
    sw = d["switch"]
    tg = d["tongue"]
    bw = sw["body_x_w"]
    by0, by1 = sw["body_y"]
    bz0, bz1 = sw["body_z"]
    sl = sw["slot"]
    out = []
    for xc in (d["x_closed"], d["x_open"]):
        b = _bx(g, xc - bw / 2, xc + bw / 2, by0, by1, bz0, bz1)
        s = _bx(g, xc - sl["w"] / 2, xc + sl["w"] / 2, by1 - sl["depth"], by1 + 1, sl["z"][0], sl["z"][1])
        b = g.cut(b, s)
        sol = g.move(g.cyl(sw["lock_d"] / 2, sw["lock_h"], "z"), xc, (by0 + by1) / 2, bz1 + sw["lock_h"] / 2)
        out.append(g.fuse(b, sol))
    xt = d["x_closed"]
    ty0, ty1 = tg["y_range"]
    out.append(_bx(g, xt - tg["w"] / 2, xt + tg["w"] / 2, ty0, ty1, tg["z"][0], tg["z"][1]))
    return g.fuse(*out)
