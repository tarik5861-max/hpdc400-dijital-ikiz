# A99 Giris govdesi 252283 (4520VQ ortak emis govdesi): ustte 4-civatali emis flansi, onde 45VQ giris destek
# plakasi yuvasi, arkada 20VQ giris destek plakasi yuvasi, ortada emis odasi; 87947 gecis ve 1296 disli delikleri.
# Lokal orijin: on yuz (A98 arka yuzu ile temas) merkezi, mil ekseni uzerinde, mil ekseni +X.


def build(d, G, g):
    bo, fr, rr, ch = d["body"], d["front_recess"], d["rear_recess"], d["suction_chamber"]
    inl, tb, cbh = d["inlet_flange"], d["tie_bolt_holes"], d["cover_bolt_holes"]
    x0, x1 = bo["local_x_range"]
    L = x1 - x0
    s = g.move(g.box(L, bo["size_yz"][0], bo["size_yz"][1]), (x0 + x1) / 2, 0, 0)
    ix0, ix1 = inl["local_x_range"]
    iz0, iz1 = inl["local_z_range"]
    pad = g.move(g.box(ix1 - ix0, inl["width_y"], iz1 - iz0), (ix0 + ix1) / 2, 0, (iz0 + iz1) / 2)
    s = g.fuse(s, pad)

    def bore(dd, xa, xb):
        return g.move(g.cyl(dd / 2, (xb - xa) + 2, "x", center=False), xa - 1, 0, 0)
    s = g.cut(s, bore(fr["d"], fr["local_x_range"][0], fr["local_x_range"][1]))
    s = g.cut(s, bore(rr["d"], rr["local_x_range"][0], rr["local_x_range"][1]))
    s = g.cut(s, bore(ch["d"], ch["local_x_range"][0] + 1, ch["local_x_range"][1] - 1))
    s = g.cut(s, bore(d["shaft_bore"]["d"], x0, x1))
    # emis agzi: flans ustunden emis odasina
    xc = (ix0 + ix1) / 2
    s = g.cut(s, g.move(g.cyl(inl["port_d"] / 2, iz1 + 1, "z", center=False), xc, 0, 0))
    # emis flansi 4 civata deligi
    bh = inl["bolt_holes"]
    for x, y in bh["centers_xy"]:
        s = g.cut(s, g.move(g.cyl(bh["d"] / 2, bh["depth"] + 1, "z", center=False), x, y, iz1 - bh["depth"]))
    # 87947 gecis delikleri (bosluklu)
    for y, z in tb["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(tb["d"] / 2, L + 2, "x", center=False), x0 - 1, y, z))
    # 1296 kapak civatasi disli delikleri (arka yuzden kor)
    for y, z in cbh["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(cbh["d"] / 2, cbh["depth"] + 1, "x", center=False), x1 - cbh["depth"], y, z))
    return s
