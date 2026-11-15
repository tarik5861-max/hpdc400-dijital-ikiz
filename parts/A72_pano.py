# A72 Elektrik panosu - dikdortgen dolap, alt yuz merkezi orijin.
# Lokal eksenler globale paralel, z 0..height. Plinth govdenin altinda, ayni taban.


def build(d, G, g):
    Lx = d["len_x"]
    Dy = d["depth_y"]
    H = d["height"]
    ph = d["plinth_height"]

    plinth = g.box(Lx, Dy, ph)
    plinth = g.move(plinth, 0, 0, ph / 2)

    body = g.box(Lx, Dy, H - ph)
    body = g.move(body, 0, 0, ph + (H - ph) / 2)

    return g.fuse(plinth, body)
