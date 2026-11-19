# Flex-side plaka - A105 (45VQ 923954) ve A111 (20VQ 923955) ortak script. Celik disk + bronz yuz (+X tarafi).
# KURAL: bronz yuz rotora bakar -> rotor arkasindaki instance rot [0,0,180] ile ters takilir.
# Lokal orijin: celik on yuz merkezi, x 0..thk_steel+bronze.thk.


def build(d, G, g):
    ts, br = d["thk_steel"], d["bronze"]
    s = g.tube(d["od"] / 2, d["bore"] / 2, ts, "x", center=False)
    bz = g.move(g.tube(br["d"] / 2, d["bore"] / 2, br["thk"], "x", center=False), ts, 0, 0)
    s = g.fuse(s, bz)
    nt = d["notches"]
    for i in range(nt["n"]):
        b = g.move(g.box(ts + 2, nt["depth"] * 2, nt["width"]), ts / 2, d["od"] / 2, 0)
        s = g.cut(s, g.rot(b, "x", nt["phase_deg"] + 360.0 * i / nt["n"]))
    return s
