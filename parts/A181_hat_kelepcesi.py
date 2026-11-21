# A181 Hat kelepcesi (A175 konsol rafina oturan omega kelepce; ikiz_tasarim varsayimi)
# Lokal orijin: boru ekseni (y=z=0), konsol X'inde ortali; boru ekseni X'e paralel.
# Ust yarim halka + ayak tarafindeki ceyrek halka; ayak raf ustune civatalanir. Olculer d[...] (instance: R, foot=+-1).
import math


def build(d, G, g):
    R, s = d["R"], 1 if d["foot"] > 0 else -1
    w, t, gap, sh, ft, fl, bd = (d[k] for k in ("strap_w", "strap_t", "gap", "shelf_gap", "foot_t", "foot_len", "bolt_d"))
    ID = R + gap
    OD = ID + t
    big = OD + 2
    ring = g.cut(g.cyl(OD, w, "x"), g.cyl(ID, w + 2, "x"))
    quad = g.move(g.box(w + 2, big, big), 0, -s * big / 2, -big / 2)              # ayagin karsi alt ceyregi
    trim = g.move(g.box(w + 2, 2 * big, big), 0, 0, -(R + sh) - big / 2)         # raf ustunden asagisi
    ring = g.cut(ring, quad, trim)
    zb, zt = -(R + sh), -(R + sh) + ft
    y0 = math.sqrt(max(ID * ID - zt * zt, 0.0)) + 1.0
    y1 = OD + fl
    foot = g.move(g.box(w, y1 - y0, ft), 0, s * (y0 + y1) / 2, (zb + zt) / 2)
    yb = s * (OD + fl * 0.55)
    bolt = g.move(g.cyl(bd / 2, ft + 13, "z"), 0, yb, zb - 8 + (ft + 13) / 2)
    return g.fuse(ring, foot, bolt)
