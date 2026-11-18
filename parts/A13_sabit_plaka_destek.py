import math


def build(d, G, g):
    # uzun kolon: on flans + cubuk + arka flans (koaksiyel X silindirleri); yerel orijin = on flans yuzu, govde -X
    parts = []
    for key, od in (("front_flange", "od"), ("rod", "d"), ("rear_flange", "od")):
        r = d[key]
        x0, x1 = r["local_x_range"]
        parts.append(g.move(g.cyl(r[od] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0))
    s = g.fuse(*parts)
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
