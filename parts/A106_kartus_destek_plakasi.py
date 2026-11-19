# Kartus destek plakasi (giris/cikis) - A106, A107 (45VQ), A112, A113 (20VQ) ortak script.
# Disk + mil deligi (burclu olanlarda delik = mil capi), rotor tarafi yuzunde kor pim delikleri ('pin_face' +x / -x),
# 2 bobrek (kidney) gecis agzi. Lokal orijin: on yuz merkezi, x 0..thk.


def build(d, G, g):
    t = d["thk"]
    s = g.tube(d["od"] / 2, d["bore"] / 2, t, "x", center=False)
    ph = d["pin_holes"]
    x0 = t - ph["depth"] if ph["face"] == "+x" else -1
    for y, z in ph["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(ph["d"] / 2, ph["depth"] + 1, "x", center=False), x0, y, z))
    kp = d["kidney_ports"]
    for y, z in kp["centers_yz"]:
        s = g.cut(s, g.move(g.cyl(kp["d"] / 2, t + 2, "x", center=False), -1, y, z))
    return s
