def build(d, G, g):
    # lokal: A54 on kafa ust yuzu merkezi (x,y), vurus ekseni z=0; ust yuz z=top_z. 4 saplama ucu (rondela+somun+uc)
    z = d["top_z"]
    out = []
    for y in d["pattern_y"]:
        w = g.move(g.cyl(d["washer_d"] / 2, d["washer_t"], "z"), 0, y, z + d["washer_t"] / 2)
        z1 = z + d["washer_t"]
        n = g.move(g.cyl(d["nut_d"] / 2, d["nut_h"], "z"), 0, y, z1 + d["nut_h"] / 2)
        z2 = z1 + d["nut_h"]
        e = g.move(g.cyl(d["stud_d"] / 2, d["stud_end_h"], "z"), 0, y, z2 + d["stud_end_h"] / 2)
        out.append(g.fuse(w, n, e))
    return g.fuse(*out)
