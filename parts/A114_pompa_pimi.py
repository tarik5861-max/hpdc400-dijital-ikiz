# A114 Kartus konum pimi 422206 (destek plakalari + halka hizalama). Instance override: d, length (45VQ / 20VQ).
# Lokal orijin: pim on ucu merkezi, eksen +X.


def build(d, G, g):
    return g.cyl(d["d"] / 2, d["length"], "x", center=False)
