# A172 Cek valf CV1 (H01 uzerinde, DN32 flansli govde, boruyu sarar)
# Lokal orijin: Boru ekseni (Y) ustunde govde merkezi; eksen Y
# Geometri d["primitives"] listesinden (box/cyl, add/cut, sirayla) kurulur; olculer params.json'dan gelir.
# Parca-bazli (dims) veya instance-bazli (A162/A175 gibi) "primitives" olabilir.
_AX = {"x": (1, 2), "y": (0, 2), "z": (0, 1)}   # eksen -> (a, b) merkez koordinat indeksleri


def _prim(g, p):
    if p["t"] == "box":
        (x0, x1), (y0, y1), (z0, z1) = p["x"], p["y"], p["z"]
        return g.move(g.box(x1 - x0, y1 - y0, z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    ax = p["axis"]
    r0, r1 = p["range"]
    s = g.cyl(p["r"], r1 - r0, ax)
    off = [0.0, 0.0, 0.0]
    ia, ib = _AX[ax]
    off[ia], off[ib] = p["c"]
    off["xyz".index(ax)] = (r0 + r1) / 2
    return g.move(s, *off)


def build(d, G, g):
    shape = None
    for p in d["primitives"]:
        s = _prim(g, p)
        if shape is None:
            shape = s
        elif p["op"] == "cut":
            shape = g.cut(shape, s)
        else:
            shape = g.fuse(shape, s)
    return shape
