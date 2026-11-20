# A124 Koruma kapisi polikarbonat paneller (2 adet, ayri solid). Lokal orijin A71 ile AYNI.


def _bx(g, x0, x1, y0, y1, z0, z1):
    s = g.box(x1 - x0, y1 - y0, z1 - z0)
    return g.move(s, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)


def build(d, G, g):
    z0, z1 = d["z_range"]
    h = d["thk"] / 2
    panes = [_bx(g, a, b, -h, h, z0, z1) for a, b in d["x_ranges"]]
    return g.fuse(panes[0], *panes[1:])
