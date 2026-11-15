def build(d, G, g):
    f, b = d["flange"], d["body"]
    def seg(dia, x0, x1):
        return g.move(g.cyl(dia / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    return g.fuse(seg(f["od"], *f["local_x_range"]), seg(b["od"], *b["local_x_range"]))
