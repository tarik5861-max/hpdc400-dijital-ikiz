# Altigen basli civata - A115 (87947, govde baglanti) ve A116 (1296, arka kapak) ortak script.
# Lokal orijin: bas alt yuzu merkezi; govde +X (0..length), bas -X (-head.h..0).
import math


def build(d, G, g):
    hd = d["head"]
    shank = g.cyl(d["d"] / 2, d["length"], "x", center=False)
    rc = hd["s"] / math.sqrt(3)   # altigen kose yaricapi
    pts = [(rc * math.cos(math.radians(30 + 60 * i)), rc * math.sin(math.radians(30 + 60 * i))) for i in range(6)]
    head = g.polyprism(pts, -hd["h"], 0)
    return g.fuse(head, shank)
