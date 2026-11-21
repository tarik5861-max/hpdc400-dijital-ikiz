# A184 Maca cekirdegi (kayar maca pimi, A167 piston kolu ucunda). Lokal orijin = A167 flans montaj yuzu merkezi;
# A167 ile ayni rot: +X dista, -X kalibin icine (rz90 -> -Y icine +Y... ) ; pozisyon = maca ILERIDE (kalibin icinde).
def build(d, G, g):
    L, r, cr, cl = d["len"], d["d"] / 2, d["collar_d"] / 2, d["collar_len"]
    pin = g.move(g.cyl(r, L, "x"), -L / 2)
    collar = g.move(g.cyl(cr, cl, "x"), -cl / 2)
    return g.fuse(pin, collar)
