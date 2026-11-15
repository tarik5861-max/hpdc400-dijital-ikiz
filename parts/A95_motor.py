def build(d, G, g):
    def seg(dia, a, b):
        return g.move(g.cyl(dia / 2, b - a, "x", center=False), a)
    ba, bb = d["body_local_x"]
    fa, fb = d["fan_cover_local_x"]
    s = g.fuse(seg(d["flange_d"], 0, d["flange_thk"]), seg(d["body_d"], ba, bb), seg(d["fan_cover_d"], fa, fb))
    tb = d["terminal_box"]
    sx, sy, sz = tb["size_xyz"]
    box = g.move(g.box(sx, sy, sz), tb["local_center_x"], 0, d["body_d"] / 2 + sz / 2)
    return g.fuse(s, box)
