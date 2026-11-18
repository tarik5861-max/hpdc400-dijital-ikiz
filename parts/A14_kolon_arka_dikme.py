def build(d, G, g):
    # levha + 2 gusset + 2 ust nervur + 2 alt nervur; yerel eksenler global ile paralel
    def rbox(xr, yr, zr):
        (x0, x1), (y0, y1), (z0, z1) = xr, yr, zr
        return g.move(g.box(x1 - x0, y1 - y0, z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    p, gu, ur, lr = d["plate"], d["gussets"], d["upper_ribs"], d["lower_ribs"]
    parts = [rbox(p["local_x_range"], p["y_range"], p["z_range"])]
    for y0, y1 in gu["y_ranges"]:
        # profil (x,z): prizma YZ'de (y=-x, z) -> X'e ekstrude (0..kalinlik) -> Z ekseni +90: x'=-y=profil x, y'=ekstrude
        pr = g.polyprism([(-x, z) for x, z in gu["profile_xz"]], 0, y1 - y0)
        parts.append(g.move(g.rot(pr, "z", 90), 0, y0, 0))
    for zr in ur["z_ranges"]:
        parts.append(rbox(ur["local_x_range"], ur["y_range"], zr))
    for yr in lr["y_ranges"]:
        parts.append(rbox(lr["local_x_range"], yr, lr["z_range"]))
    return g.fuse(*parts)
