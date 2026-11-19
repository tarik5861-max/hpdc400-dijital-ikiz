# A100 Arka kapak 20VQ (4-civatali kapak 250824 / 4520VQ**A**): 20VQ kartus yuvasi, ustte P2 cikis agzi,
# Y ekseninde emniyet valfi yuvasi (A117 valf + A118 yay + 2x A119 tapa), 4x 1296 civata gecis deligi.
# Lokal orijin: on yuz (A99 arka yuzu ile temas) merkezi, mil ekseni uzerinde, mil ekseni +X.


def build(d, G, g):
    bo, cb, op, vb, bh = d["body"], d["cartridge_bore"], d["outlet_port"], d["valve_bore"], d["bolt_holes"]
    x0, x1 = bo["local_x_range"]
    L = x1 - x0
    wy, hz = bo["size_yz"]
    s = g.move(g.box(L, wy, hz), (x0 + x1) / 2, 0, 0)
    px0, px1 = op["boss_local_x_range"]
    pz0, pz1 = op["boss_local_z_range"]
    s = g.fuse(s, g.move(g.box(px1 - px0, op["boss_width_y"], pz1 - pz0), (px0 + px1) / 2, 0, (pz0 + pz1) / 2))
    c0, c1 = cb["local_x_range"]
    s = g.cut(s, g.move(g.cyl(cb["d"] / 2, (c1 - c0) + 1, "x", center=False), c0 - 1, 0, 0))
    # P2 cikis agzi: ustten kartus yuvasina
    s = g.cut(s, g.move(g.cyl(op["d"] / 2, pz1 + 1, "z", center=False), (px0 + px1) / 2, 0, 0))
    # emniyet valfi yuvasi (Y boyunca boydan boya)
    vx, vz = vb["center_xz"]
    s = g.cut(s, g.move(g.cyl(vb["d"] / 2, wy + 2, "y"), vx, 0, vz))
    for y, z in bh["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(bh["d"] / 2, L + 2, "x", center=False), x0 - 1, y, z))
    return s
