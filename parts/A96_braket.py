def build(d, G, g):
    def blk(r):
        (x0, x1), (y0, y1), (z0, z1) = r["local_x"], r["y"], r["local_z"]
        return g.move(g.box(x1 - x0, y1 - y0, z1 - z0), (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    return g.fuse(blk(d["plate"]), blk(d["arm"]))
