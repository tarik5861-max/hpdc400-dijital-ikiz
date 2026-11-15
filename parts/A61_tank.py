# A61 Hidrolik tank - solid box (tank modeli: "may be drawn as solid box").
# Lokal orijin: alt yuz merkezi. Eksenler globale paralel, z 0..height.


def build(d, G, g):
    L = d["len_x"]
    W = d["width_y"]
    H = d["height"]
    # Merkezli kutu, sonra alt yuz orijine gelsin diye z'de H/2 yukari.
    tank = g.box(L, W, H)
    tank = g.move(tank, 0, 0, H / 2)
    return tank
