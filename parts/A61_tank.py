"""
A61_tank.py - Hidrolik tank (sase A11 icinde, 2026-11-19). Govde kutu + -Y yuzunde erisim elemanlari:
(yon side_face_y isaretinden) gozlem cami, civatali yan kapak, dolum/hava filtresi, donus filtresi kapagi. Tum olculer params A61.dims.
Lokal orijin: alt yuz merkezi; z 0..height; erisim yuzu y = side_face_y (+Y ya da -Y).
"""


def build(d, G, g):
    L, W, H = d["len_x"], d["width_y"], d["height"]
    yf = d["side_face_y"]
    sgn = 1 if yf > 0 else -1
    body = g.move(g.box(L, W, H), 0, 0, H / 2)

    def pad(x_rng, z_rng, t):   # erisim yuzune yapisik dikdortgen eleman (disa dogru t)
        x0, x1 = x_rng
        z0, z1 = z_rng
        return g.move(g.box(x1 - x0, t, z1 - z0), (x0 + x1) / 2, yf + sgn * t / 2, (z0 + z1) / 2)

    sg, sc = d["sight_glass"], d["side_cover"]
    parts = [pad(sg["local_x_range"], sg["local_z_range"], sg["protrude"]),
             pad(sc["local_x_range"], sc["local_z_range"], sc["thk"])]
    for k in ("filler_breather", "return_filter_cap"):
        c = d[k]
        x, z = c["local_xz"]
        parts.append(g.move(g.cyl(c["d"] / 2, c["length"], "y", center=False), x, yf if sgn > 0 else yf - c["length"], z))
    return g.fuse(body, *parts)
