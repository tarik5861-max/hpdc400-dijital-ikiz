# Kartus halkasi (cam ring) - A102 (45VQ) ve A108 (20VQ) ortak script. Ic profil cift loblu kam:
# r(t) = (Rmaj+Rmin)/2 + (Rmaj-Rmin)/2*cos(2t), t = +Y'den +Z'ye aci. Eksenel pim delikleri.
# Lokal orijin: on yuz merkezi, eksen +X, x 0..width.
import math


def build(d, G, g):
    w = d["width"]
    cam = d["cam"]
    s = g.move(g.cyl(d["od"] / 2, w, "x", center=False), 0, 0, 0)
    a, b = (cam["r_major"] + cam["r_minor"]) / 2, (cam["r_major"] - cam["r_minor"]) / 2
    n = cam["n_pts"]
    pts = []
    for i in range(n):
        t = 2 * math.pi * i / n
        r = a + b * math.cos(2 * t)
        pts.append((r * math.cos(t), r * math.sin(t)))
    s = g.cut(s, g.polyprism(pts, -1, w + 1))
    ph = d["pin_holes"]
    for y, z in ph["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(ph["d"] / 2, w + 2, "x", center=False), -1, y, z))
    return s
