def build(d, G, g):
    # lokal: kamara arka uc yuzu merkezi (x=0), vurus ekseni; boru -X yonunde x -L..0; +Y'de mikne kolu icin yarik
    L, ro, ri = d["length"], d["od"] / 2, d["id"] / 2
    s = g.move(g.tube(ro, ri, L, "x"), -L / 2, 0, 0)
    c = d["end_collar"]
    s = g.fuse(s, g.move(g.tube(c["od"] / 2, ri, c["length"], "x"), -L + c["length"] / 2, 0, 0))
    sl = d["slot"]
    s = g.cut(s, g.move(g.box(L + 2, c["od"], sl["width_z"], True), -L / 2, c["od"] / 2, 0))
    return s
