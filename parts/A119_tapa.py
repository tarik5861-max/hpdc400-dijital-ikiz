# A119 Tapa 7077 (emniyet valfi yuvasini iki ucta kapatir). Dis yuzde altigen lokma yuvasi.
# Lokal orijin: dis yuz merkezi, eksen +X (yuvanin icine).
import math


def build(d, G, g):
    s = g.cyl(d["d"] / 2, d["length"], "x", center=False)
    so = d["socket"]
    rc = so["s"] / math.sqrt(3)
    pts = [(rc * math.cos(math.radians(60 * i)), rc * math.sin(math.radians(60 * i))) for i in range(6)]
    return g.cut(s, g.polyprism(pts, -1, so["depth"]))
