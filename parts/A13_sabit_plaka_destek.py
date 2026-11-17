def build(d, G, g):
    # taban + kolon plakasi + 2 ucgen gusset (profile_xz, Y kalinligi)
    b = d["base_plate"]; c = d["column_plate"]; gu = d["gussets"]
    def rbox(r):
        (x0, x1), (y0, y1), (z0, z1) = r["local_x_range"], r["y_range"], r["z_range"]
        return g.move(g.box(x1 - x0, y1 - y0, z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    s = g.fuse(rbox(b), rbox(c))
    for y0, y1 in gu["y_ranges"]:
        # prizma: Y=profil x, Z=profil z, X=kalinlik; Z ekseni -90 deg: (x,y)->(y,-x)
        pr = g.polyprism([(x, z) for x, z in gu["profile_xz"]], 0, y1 - y0)
        pr = g.rot(pr, "z", -90)          # kalinlik y: 0..-(y1-y0)
        s = g.fuse(s, g.move(pr, 0, y1, 0))
    return s
