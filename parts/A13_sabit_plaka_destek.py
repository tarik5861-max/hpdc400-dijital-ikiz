"""
A13_sabit_plaka_destek.py — Sabit plaka destek kolonu (3 adet: 2 alt, 1 üst).
Ön flanş (A21'e cıvatalı), çubuk (silindir) ve arka flanş (A14'e kaynaklı).
Şimdi ön flanş bağlantısı cıvatalı (M24 cıvata delikleri ve montaj yüzü detaylı) tasarlandı.
"""
import math


def build(d, G, g):
    # uzun kolon: on flans + cubuk + arka flans; yerel orijin = on flans yuzu, govde -X
    parts = []
    for key, od in (("front_flange", "od"), ("rod", "d"), ("rear_flange", "od")):
        r = d[key]
        x0, x1 = r["local_x_range"]
        parts.append(g.move(g.cyl(r[od] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0))
    s = g.fuse(*parts)

    # Ön flanş cıvata delikleri (M24, PCD üzerinden)
    ff = d["front_flange"]
    b = ff.get("bolts")
    if b:
        x0, x1 = ff["local_x_range"]
        holes = []
        for i in range(int(b["count"])):
            a = math.radians(b["start_angle_deg"] + i * 360.0 / b["count"])
            holes.append(g.move(g.cyl(b["hole_d"] / 2, x1 - x0 + 2, "x"),
                                (x0 + x1) / 2, b["pcd"] / 2 * math.cos(a), b["pcd"] / 2 * math.sin(a)))
        s = g.cut(s, *holes)

    return s
