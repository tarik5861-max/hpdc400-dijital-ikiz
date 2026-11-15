def build(d, G, g):
    fh, ba, rh, rod = d["front_head"], d["barrel"], d["rear_head"], d["rod"]
    def blk(h):
        x0, x1 = h["local_x_range"]
        return g.move(g.box(x1 - x0, h["size_yz"][0], h["size_yz"][1]), (x0 + x1) / 2, 0, 0)
    x0, x1 = ba["local_x_range"]
    barrel = g.move(g.tube(ba["od"] / 2, ba["bore"] / 2, x1 - x0, "x"), (x0 + x1) / 2, 0, 0)
    fx0 = fh["local_x_range"][0]
    rl = -fx0 + rod["protrusion_plus_x"]
    rodc = g.move(g.cyl(rod["d"] / 2, rl, "x"), (fx0 + rod["protrusion_plus_x"]) / 2, 0, 0)
    return g.fuse(blk(fh), blk(rh), barrel, rodc)
