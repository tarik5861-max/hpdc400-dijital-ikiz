def build(d, G, g):
    # lokal orijin: vurus ekseni yuksekligi, x/y = vericinin ekseni; taban z = z_off (instance bazli)
    z = d["z_off"]
    hx = g.move(g.cyl(d["hex_d"] / 2, d["hex_h"], "z"), 0, 0, z + d["hex_h"] / 2)
    bd = g.move(g.cyl(d["d"] / 2, d["h"] - d["hex_h"], "z"), 0, 0, z + d["hex_h"] + (d["h"] - d["hex_h"]) / 2)
    return g.fuse(hx, bd)
