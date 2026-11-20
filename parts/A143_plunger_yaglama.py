def build(d, G, g):
    # lokal: A141 hunisi ile ayni orijin (dolum agzi merkezi x,y; vurus ekseni z=0). Lubrikator -Y yani.
    pl, sh, rs, cp = d["plate"], d["shelf"], d["reservoir"], d["cap"]
    def bx(xh, y0, y1, z0, z1):
        return g.move(g.box(2 * xh, y1 - y0, z1 - z0), 0, (y0 + y1) / 2, (z0 + z1) / 2)
    parts = [bx(pl["x_half"], *pl["y"], *pl["z"]), bx(sh["x_half"], *sh["y"], *sh["z"])]
    z0, z1 = rs["z"]
    parts.append(g.move(g.cyl(rs["d"] / 2, z1 - z0, "z"), 0, rs["y_c"], (z0 + z1) / 2))
    parts.append(g.move(g.cyl(cp["d"] / 2, cp["h"], "z"), 0, rs["y_c"], z1 + cp["h"] / 2))
    # dozaj nipeli: rezervuar altindan bracket'a bakan kisa boru (yaglama hatti)
    ln = d["line"]
    parts.append(g.move(g.cyl(ln["d"] / 2, ln["len"], "y"), 0, ln["y_c"], ln["z"]))
    return g.fuse(*parts)
