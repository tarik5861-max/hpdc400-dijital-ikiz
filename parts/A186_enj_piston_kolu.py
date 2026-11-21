# A186 Enjeksiyon piston + kol grubu (A54 hidrolik silindirinin hareketli ic grubu; A52 plunger ile birlikte +X ilerler).
# Lokal orijin = A54 lokal orijini (on kafa on yuzu merkezi), A54_1 ile ayni pos/rot. Retracted: kol on ucu x=+protrusion_plus_x
# (A52 baglanti arka yuzune degen), piston diski barrel icinde en arkada. Olculer params.A186.dims (A54/A52 dims'ten TURETILMIS).
def build(d, G, g):
    rod, pis = d["rod"], d["piston"]
    x0, x1 = rod["x_range"]
    rodc = g.move(g.cyl(rod["d"] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    p0, p1 = pis["x_range"]
    disc = g.move(g.cyl(pis["d"] / 2, p1 - p0, "x"), (p0 + p1) / 2, 0, 0)
    return g.fuse(rodc, disc)
