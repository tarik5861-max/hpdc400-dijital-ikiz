# A117 Emniyet (relief) valfi kartusu 2327xx S/A (A100 valf yuvasinda). Govde + boyun (tahliye bolgesi).
# Lokal orijin: tapa tarafi uc yuzu merkezi, eksen +X (yay yonune).


def build(d, G, g):
    L = d["length"]
    nk = d["neck"]
    a, b = nk["local_x_range"]
    s = g.cyl(d["d"] / 2, L, "x", center=False)
    groove = g.move(g.tube(d["d"] / 2 + 1, nk["d"] / 2, b - a, "x", center=False), a, 0, 0)
    return g.cut(s, groove)
