# A98 Pompa on govde (Vickers/Eaton 4520VQ - 45VQ kismi): montaj flansi + pilot, mil yatagi, 45VQ kartus yuvasi, P1 cikis agzi.
# Lokal orijin: montaj flansi on yuzu (kampana ile temas) merkezi, mil ekseni uzerinde. Mil ekseni lokal +X (motordan uzaga).


def _xr(r):
    return r[0], r[1], r[1] - r[0]


def build(d, G, g):
    pl, fl, bo = d["pilot"], d["flange"], d["body"]
    cb, sb, op, tb = d["cartridge_bore"], d["shaft_bore"], d["outlet_port"], d["tie_bolt_holes"]

    x0, x1, L = _xr(pl["local_x_range"])
    pilot = g.move(g.cyl(pl["d"] / 2, L, "x", center=False), x0, 0, 0)
    x0, x1, L = _xr(fl["local_x_range"])
    flange = g.move(g.box(L, fl["size_yz"][0], fl["size_yz"][1]), (x0 + x1) / 2, 0, 0)
    x0, x1, L = _xr(bo["local_x_range"])
    body = g.move(g.box(L, bo["size_yz"][0], bo["size_yz"][1]), (x0 + x1) / 2, 0, 0)
    bx0, bx1, _ = _xr(op["boss_local_x_range"])
    by0 = op["boss_y_min"]
    by1 = -bo["size_yz"][0] / 2
    boss = g.move(g.box(bx1 - bx0, by1 - by0, op["boss_size_z"]), (bx0 + bx1) / 2, (by0 + by1) / 2, 0)
    s = g.fuse(pilot, flange, body, boss)

    # bosluklar
    x0, x1, L = _xr(cb["local_x_range"])
    s = g.cut(s, g.move(g.cyl(cb["d"] / 2, L + 1, "x", center=False), x0, 0, 0))
    x0, x1, L = _xr(sb["local_x_range"])
    s = g.cut(s, g.move(g.cyl(sb["d"] / 2, L + 2, "x", center=False), x0 - 1, 0, 0))
    # P1 cikis agzi: -Y yuzunden kartus yuvasina
    port_len = -by0 - cb["d"] / 2 + 5
    port = g.move(g.cyl(op["d"] / 2, port_len + 1, "y", center=False), (bx0 + bx1) / 2, by0 - 1, 0)
    s = g.cut(s, port)
    # flans baglanti delikleri (kampanaya)
    fx0, fx1, fL = _xr(fl["local_x_range"])
    for y, z in fl["bolt_holes"]["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(fl["bolt_holes"]["d"] / 2, fL + 2, "x", center=False), fx0 - 1, y, z))
    # 87947 baglanti civatasi disli delikleri (arka yuzden kor)
    for y, z in tb["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(tb["d"] / 2, tb["depth"] + 1, "x", center=False), bo["local_x_range"][1] - tb["depth"], y, z))
    return s
