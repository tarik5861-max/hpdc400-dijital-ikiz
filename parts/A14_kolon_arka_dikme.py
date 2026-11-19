"""
A14_kolon_arka_dikme.py — Şase arka ucundaki ana dikme ve destek yapısı (Modern Endüstriyel Tasarım).
Optimize edilmiş kütle, pahlanmış köşeler, estetik hafifletme ceppleri ve sağlam mesnet yapısı.
"""
def build(d, G, g):
    # tek parca kalin govde: XZ yan profili (Y boyunca ekstrude) ∩ YZ pahli siluet (X boyunca ekstrude)
    b = d["body"]
    y0, y1 = b["y_range"]
    side = g.polyprism([(-x, z) for x, z in b["profile_xz"]], 0, y1 - y0)
    side = g.move(g.rot(side, "z", 90), 0, y0, 0)
    xs = [x for x, _ in b["profile_xz"]]
    zt = max(z for _, z in b["profile_xz"])
    c = b["top_corner_chamfer"]
    pts = [(y0, 0), (y1, 0), (y1, zt - c), (y1 - c, zt), (y0 + c, zt), (y0, zt - c)]
    sil = g.polyprism(pts, min(xs) - 1, max(xs) + 1)
    body = g.common(side, sil)
    # on yuzden sase ustune ucgen kaburgalar (taban baglantisi; d["ribs"])
    r = d.get("ribs")
    if not r:
        return body
    x0, x1 = r["x_local_range"]   # on yuz (lokal 50) .. uc (lokal 700 = X -2000)
    tri = [(x0, 0), (x1, 0), (x0, r["height"])]
    for ya, yb in r["y_ranges"]:
        lo, hi = min(ya, yb), max(ya, yb)
        rib = g.polyprism([(-x, z) for x, z in tri], 0, hi - lo)
        body = g.fuse(body, g.move(g.rot(rib, "z", 90), 0, lo, 0))
    return body
